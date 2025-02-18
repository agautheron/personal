# Comment installer le gestionnaire de mots de passe Passbolt sur Ubuntu 24.04 Server

*Dernière mise à jour : 18 février 2025 par Arthur Gautheron (Admin)*

Passbolt est un gestionnaire de mots de passe open-source auto-hébergé, qui vous permet de stocker et de partager en toute sécurité des identifiants de connexion pour des sites web, des routeurs, des réseaux Wi-Fi, etc. Ce tutoriel vous montrera comment installer Passbolt Community Edition (CE) sur Ubuntu 24.04 avec le serveur web Apache.

## Fonctionnalités de Passbolt

- Gratuit et open-source
- Les mots de passe sont chiffrés avec [OpenPGP](https://fr.wikipedia.org/wiki/Pretty_Good_Privacy), une norme cryptographique éprouvée.
- Des extensions de navigateur sont disponibles pour Firefox, Google Chrome, Microsoft Edge et Brave.
- Une application mobile est disponible pour iOS et Android.
- Partage facile des identifiants de connexion avec votre équipe sans compromettre la sécurité.
- Interface propre et conviviale.
- Importation et exportation des mots de passe. Vous pouvez exporter vos mots de passe au format `.kdbx` ou `.csv` pour les utiliser avec KeepassX, LastPass ou 1Password.
- Possibilité d'ajouter manuellement des identifiants de connexion.

## Prérequis pour l'installation de Passbolt sur Ubuntu 24.04 Server

Passbolt est écrit en PHP et repose sur un serveur de base de données MySQL/MariaDB. Vous devez donc configurer une pile LAMP ou LEMP avant d'installer Passbolt.

- Ici j'ai choisi le serveur web Apache, mais vous pouvez aussi choisir un serveur Nginx.

- Il est très important que votre serveur puisse envoyer des e-mails, afin que vous puissiez récupérer votre compte Passbolt en cas d'oubli du mot de passe.

- Vous avez également besoin d'un nom de domaine, afin de pouvoir accéder en toute sécurité à Passbolt depuis n'importe où avec un navigateur web.

Une fois que les exigences ci-dessus sont remplies, suivez les instructions ci-dessous pour installer Passbolt.

## Étape 1 : Télécharger Passbolt sur votre serveur Ubuntu 24.04

Si vous allez sur le site officiel pour télécharger Passbolt, il vous sera demandé de saisir votre nom et votre adresse e-mail. Si vous ne souhaitez pas le faire, téléchargez la dernière version stable depuis Github en exécutant les commandes suivantes sur votre serveur.

```bash
sudo apt install git

sudo mkdir -p /var/www/

sudo chown www-data:www-data /var/www/ -R

cd /var/www/

sudo -u www-data git clone https://github.com/passbolt/passbolt_api.git
```

Les fichiers seront enregistrés dans le répertoire `passbolt_api`. Renommez-le en `passbolt`.

```bash
sudo mv passbolt_api passbolt
```

Ensuite, attribuez l'utilisateur du serveur web (`www-data`) comme propriétaire de ce répertoire.

```bash
sudo chown -R www-data:www-data /var/www/passbolt

sudo chown -Rf root:www-data /var/www/passbolt/config/jwt/

sudo chmod 750 /var/www/passbolt/config/jwt/

sudo chmod 640 /var/www/passbolt/config/jwt/jwt.key

sudo chmod 640 /var/www/passbolt/config/jwt/jwt.pem
```

Exécutez la commande suivante pour installer les modules PHP requis ou recommandés par Passbolt.

```bash
sudo apt install php-imagick php-gnupg php8.3-gnupg php8.3-common php8.3-mysql php8.3-fpm php8.3-ldap php8.3-gd php8.3-imap php8.3-curl php8.3-zip php8.3-xml php8.3-mbstring php8.3-bz2 php8.3-intl php8.3-gmp php8.3-xsl
```

Ensuite, redémarrez Apache. (Si vous utilisez Nginx, vous n'avez pas besoin de redémarrer Nginx.)

```bash
sudo systemctl restart apache2
```

Changez de répertoire.

```bash
cd /var/www/passbolt/
```

Installez Composer – le gestionnaire de dépendances PHP.

```bash
sudo apt install composer
```

Créez un répertoire de cache pour Composer.

```bash
sudo mkdir /var/www/.composer
```

Attribuez `www-data` comme propriétaire.

```bash
sudo chown -R www-data:www-data /var/www/.composer
```

Utilisez Composer pour installer les dépendances.

```bash
sudo -u www-data composer install --no-dev
```

Si on vous demande de définir les permissions des dossiers, choisissez `Y`.

## Étape 2 : Créer une base de données MariaDB et un utilisateur pour Passbolt

Connectez-vous à la console MariaDB.

```bash
sudo mysql -u root
```

Ensuite, créez une nouvelle base de données pour Passbolt en utilisant la commande suivante. Ce tutoriel la nomme `passbolt`, mais vous pouvez utiliser le nom que vous souhaitez pour la base de données. Nous spécifions également `utf8mb4` comme jeu de caractères pour prendre en charge les caractères non latins et les emojis.

```sql
CREATE DATABASE passbolt DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

La commande suivante créera un utilisateur de base de données appelé `passboltuser`. Remplacez `password` par votre mot de passe sécurisé.

```sql
CREATE USER 'passboltuser'@'localhost' IDENTIFIED BY 'password';
```

Ensuite, accordez tous les privilèges sur la base de données `passbolt` à l'utilisateur `passboltuser`.

```sql
GRANT ALL PRIVILEGES ON passbolt.* TO 'passboltuser'@'localhost';
```

Rechargez les tables de privilèges et quittez.

```sql
FLUSH PRIVILEGES;

EXIT;
```

## Étape 3 : Générer une clé OpenPGP

Passbolt utilise OpenPGP pour chiffrer les mots de passe. Nous devons générer une paire de clés GPG pour le serveur Passbolt.

1. **Installer le paquet haveged (optionnel mais recommandé)**

   Si vous utilisez un serveur VPS, il est recommandé d'installer le paquet `haveged` pour générer suffisamment d'entropie :

   ```bash
   sudo apt install haveged
   ```

   Le service `haveged` démarrera automatiquement après l'installation. Vous pouvez vérifier son statut avec :

   ```bash
   sudo systemctl status haveged
   ```

2. **Générer une nouvelle paire de clés GPG**

   Exécutez la commande suivante pour générer une nouvelle paire de clés GPG :

   ```bash
   sudo -u www-data gpg --quick-gen-key --pinentry-mode=loopback 'Prénom Nom <vous@example.com>' default default never
   ```

   Remplacez `Prénom Nom` par votre prénom et nom, et `vous@example.com` par votre adresse e-mail réelle. N'oubliez pas de conserver les chevrons (`<` et `>`).

   Par exemple :

   ```bash
   sudo -u www-data gpg --quick-gen-key --pinentry-mode=loopback 'Jean Dupont <jean.dupont@example.com>' default default never
   ```

   Si l'on vous demande de définir une phrase de passe, appuyez simplement sur Entrée pour la laisser vide, car le module `php-gnupg` ne supporte pas l'utilisation de phrases de passe pour le moment.

3. **Exporter la clé privée vers le répertoire de configuration de Passbolt**

   Copiez la clé privée dans le répertoire de configuration de Passbolt :

   ```bash
   sudo -u www-data gpg --armor --export-secret-keys vous@example.com | sudo tee /var/www/passbolt/config/gpg/serverkey_private.asc > /dev/null
   ```

   Remplacez `vous@example.com` par l'adresse e-mail utilisée lors de la génération de la clé.

4. **Exporter la clé publique**

   Copiez également la clé publique :

   ```bash
   sudo -u www-data gpg --armor --export vous@example.com | sudo tee /var/www/passbolt/config/gpg/serverkey.asc > /dev/null
   ```

   Assurez-vous que les fichiers de clés ont les permissions appropriées :

   ```bash
   sudo chown -R www-data:www-data /var/www/passbolt/config/gpg/
   sudo chmod 440 /var/www/passbolt/config/gpg/serverkey_private.asc
   sudo chmod 440 /var/www/passbolt/config/gpg/serverkey.asc
   ```

Vos clés GPG sont maintenant prêtes à être utilisées avec Passbolt.


## Étape 4 : Configurer le serveur web

### Pour Apache

1. **Activer les modules requis :**

   ```bash
   sudo a2enmod ssl
   sudo a2enmod rewrite
   ```

2. **Créer un hôte virtuel pour Passbolt :**

   Créez un fichier de configuration pour le site Passbolt :

   ```bash
   sudo nano /etc/apache2/sites-available/passbolt.conf
   ```

   Ajoutez-y le contenu suivant, en remplaçant `passbolt.votre_domaine.com` par votre nom de domaine réel :

   ```apache
   <VirtualHost *:80>
       ServerName passbolt.votre_domaine.com
       DocumentRoot /var/www/passbolt

       <Directory /var/www/passbolt>
           Options FollowSymLinks
           AllowOverride All
           Require all granted
       </Directory>

       ErrorLog ${APACHE_LOG_DIR}/passbolt_error.log
       CustomLog ${APACHE_LOG_DIR}/passbolt_access.log combined
   </VirtualHost>
   ```

3. **Activer le site et redémarrer Apache :**

   ```bash
   sudo a2ensite passbolt.conf
   sudo systemctl reload apache2
   ```

### Pour Nginx

1. **Créer un bloc serveur pour Passbolt :**

   Créez un fichier de configuration pour le site Passbolt :

   ```bash
   sudo nano /etc/nginx/sites-available/passbolt
   ```

   Ajoutez-y le contenu suivant, en remplaçant `passbolt.votre_domaine.com` par votre nom de domaine réel :

   ```nginx
   server {
       listen 80;
       server_name votre_domaine.com;

       root /var/www/passbolt;
       index index.php index.html;

       location / {
           try_files $uri $uri/ /index.php?$args;
       }

       location ~ \.php$ {
           include snippets/fastcgi-php.conf;
           fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
       }

       location ~ /\.ht {
           deny all;
       }
   }
   ```

2. **Activer le site et redémarrer Nginx :**

   ```bash
   sudo ln -s /etc/nginx/sites-available/passbolt /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   ```

## Étape 5 : Configurer HTTPS avec Let's Encrypt

Il est essentiel de sécuriser votre site avec HTTPS.

### Pour Apache

1. **Installer Certbot :**

   ```bash
   sudo apt install certbot python3-certbot-apache
   ```

2. **Obtenir et installer le certificat SSL :**

   ```bash
   sudo certbot --apache -d votre_domaine.com
   ```

   Suivez les instructions à l'écran pour compléter l'installation.

### Pour Nginx

1. **Installer Certbot :**

   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtenir et installer le certificat SSL :**

   ```bash
   sudo certbot --nginx -d votre_domaine.com
   ```

   Suivez les instructions à l'écran pour compléter l'installation.

## Étape 6 : Finaliser l'installation de Passbolt

1. **Configurer Passbolt :**

   Copiez le fichier de configuration par défaut :

   ```bash
   sudo cp /var/www/passbolt/config/passbolt.default.php /var/www/passbolt/config/passbolt.php
   ```

   Éditez le fichier de configuration :

   ```bash
   sudo nano /var/www/passbolt/config/passbolt.php
   ```

   Modifiez les sections suivantes :

   - **App** : Remplacez `'fullBaseUrl'` par votre domaine, par exemple `'https://passbolt.votre_domaine.com'`. N'oubliez pas de créer un enregistrement DNS A pour ce sous-domaine dans votre éditeur de zone DNS.
   - **Database** : Renseignez les informations de connexion à la base de données que vous avez créées précédemment. 
   
   ```php
   // Database configuration.
    'Datasources' => [
        'default' => [
            'host' => 'localhost',
            //'port' => 'non_standard_port_number',
            'username' => 'user',
            'password' => 'secret',
            'database' => 'passbolt',
        ],
    ],
   ```
   - **Email**:Dans la section de configuration du courrier électronique, spécifiez le nom d'hôte SMTP, le numéro de port, les identifiants de connexion, afin que votre passbolt puisse envoyer des courriels. En général, vous devez utiliser le port 587 pour envoyer des courriels à un serveur SMTP distant. Assurez-vous de mettre tls à true, afin que la transaction SMTP soit cryptée. Définissez également l'adresse e-mail From : et le nom From.
   ```php
    // Email configuration.
    'EmailTransport' => [
        'default' => [
            'host' => 'smtp-relay.sendinblue.com',
            'port' => 587,
            'username' => 'smtp_username',
            'password' => 'smtp_password',
            // Is this a secure connection? true if yes, null if no.
            'tls' => true,
            //'timeout' => 30,
            //'client' => null,
            //'url' => null,
        ],
    ],
    'Email' => [
        'default' => [
            // Defines the default name and email of the sender of the emails.
            'from' => ['passbolt@example.com' => 'Passbolt'],
            //'charset' => 'utf-8',
            //'headerCharset' => 'utf-8',
        ],
    ],
	```
	![email](/img/projects/passbolt/passbolt-send-email.webp)
   - **GPG** : 
Dans la section gpg, entrez l'empreinte de la clé GPG comme ci-dessous. Vous devez supprimer tous les espaces dans l'empreinte.

	```php
	'fingerprint' => '2FC8945833C51946E937F9FED47B0811573EE67E',
	```

Vous pouvez obtenir l'empreinte de votre clé à l'aide de la commande suivante. Remplacez passbolt@example.com par votre adresse électronique lors de la génération de la paire de clés PGP.

	```bash
	sudo su -s /bin/bash -c « gpg --list-keys » www-data
	```
passbolt-gpg-key-fingerprint.webp
Après avoir saisi l'empreinte digitale, décommentez les deux lignes suivantes.

	```php
'public' => CONFIG . 'gpg' . DS . 'serverkey.asc',
'private' => CONFIG . 'gpg' . DS . 'serverkey_private.asc',
	```
	![gpg](/img/projects/passbolt/passbolt-gpg-configuration.webp)
	
   - **SSl** : Ajouter le bloc *ssl* à la fin de la partie que vous venez de configurer
  :
	```php
	'passbolt' => [
        // GPG Configuration.
        // The keyring must to be owned and accessible by the webserver user.
        // Example: www-data user on Debian
        'gpg' => [
            // Tell GPG where to find the keyring.
            // If putenv is set to false, gnupg will use the default path ~/.gnupg.
            // For example :
            // - Apache on Centos it would be in '/usr/share/httpd/.gnupg'
            // - Apache on Debian it would be in '/var/www/.gnupg'
            // - Nginx on Centos it would be in '/var/lib/nginx/.gnupg'
            // - etc.
            //'keyring' => getenv("HOME") . DS . '.gnupg',
            //
            // Replace GNUPGHOME with above value even if it is set.
            //'putenv' => false,

            // Main server key.
            'serverKey' => [
                // Server private key fingerprint.
                'fingerprint' => '8447C5DD8077B73760CAB194874DE4C6C4562E70',
                'public' => CONFIG . 'gpg' . DS . 'serverkey.asc',
                'private' => CONFIG . 'gpg' . DS . 'serverkey_private.asc',
            ],
        ],
        'ssl' =>[
            'force' => true,
        ],
    ],
	```

2. **Configurer les permissions :**

   ```bash
   sudo chown -R www-data:www-data /var/www/passbolt/
   sudo chmod 600 /var/www/passbolt/config/passbolt.php
   ```
3. **Exécuter le script d'installation:**
Exécutez le script d'installation en tant qu'utilisateur www-data.

   ```bash
	sudo su -s /bin/bash -c « /var/www/passbolt/bin/cake passbolt install --force » www-data
   ```

Pendant l'installation, il vous sera demandé de créer un compte administrateur.

![install](/img/projects/passbolt/install-passbolt-ubuntu.webp)

Une fois le compte créé, vous recevrez une URL vous permettant de terminer l'installation dans un navigateur web.

4. **Vérifier l'installation :**

   Utilisez la commande suivante pour vérifier que tout est correctement configuré :

   ```bash
   sudo -u www-data /var/www/passbolt/bin/cake passbolt healthcheck
   ```

   Si tout est en ordre, vous devriez voir des messages indiquant que les tests sont réussis.

5. **Accéder à Passbolt :**

   Ouvrez un navigateur et rendez-vous sur `https://passbolt.votre_domaine.com`. Suivez les instructions à l'écran pour créer votre compte administrateur et commencer à utiliser Passbolt.