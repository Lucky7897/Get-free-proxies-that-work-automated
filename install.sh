
### `install_linux_gui.sh`

```bash
#!/bin/bash

# Script to install GUI on a Linux command-line machine

# Ensure the script is run with superuser privileges
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
fi

# Prompt for username and password
echo "Please enter your username:"
read username
echo "Please enter your password:"
read -s password

# List of top 15 Linux distributions
declare -a distros=("Ubuntu" "Debian" "Fedora" "CentOS" "Arch Linux" "OpenSUSE" "Kali Linux" "Linux Mint" "Manjaro" "Pop!_OS" "Elementary OS" "Zorin OS" "MX Linux" "Solus" "PCLinuxOS")

# Function to update package list and install GUI based on distro
install_gui() {
    case $1 in
        "Ubuntu"|"Debian")
            apt-get update
            apt-get install -y ubuntu-desktop
            ;;
        "Fedora")
            dnf install -y @cinnamon-desktop-environment
            ;;
        "CentOS")
            yum groupinstall -y "GNOME Desktop"
            ;;
        "Arch Linux")
            pacman -Syu
            pacman -S --noconfirm gnome
            ;;
        "OpenSUSE")
            zypper install -t pattern gnome
            ;;
        # Add other distros here...
        *)
            echo "Distribution not supported yet."
            ;;
    esac
}

# Prompt for Linux distribution
echo "Which Linux do you want to install GUI on? (Choose a number)"
select distro in "${distros[@]}"; do
    echo "Installing GUI for $distro..."
    install_gui $distro
    break
done

# Prompt for SSH configuration
echo "Do you want to adjust SSH to public key or to username/password authorization? (publickey/usernamepassword)"
read ssh_config

# Function to adjust SSH settings
adjust_ssh() {
    case $1 in
        "publickey")
            sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
            systemctl restart sshd
            ;;
        "usernamepassword")
            sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
            systemctl restart sshd
            ;;
        *)
            echo "Invalid option. SSH settings not changed."
            ;;
    esac
}

adjust_ssh $ssh_config

# Prompt for RDP/VNC activation
echo "Do you want to activate RDP or VNC? (rdp/vnc/none)"
read remote_access

# Function to install and configure RDP/VNC
setup_remote_access() {
    case $1 in
        "rdp")
            case $distro in
                "Ubuntu"|"Debian")
                    apt-get install -y xrdp
                    systemctl enable xrdp
                    systemctl start xrdp
                    ;;
                "Fedora")
                    dnf install -y xrdp
                    systemctl enable xrdp
                    systemctl start xrdp
                    ;;
                "CentOS")
                    yum install -y epel-release
                    yum install -y xrdp
                    systemctl enable xrdp
                    systemctl start xrdp
                    ;;
                "Arch Linux")
                    pacman -S --noconfirm xrdp
                    systemctl enable xrdp
                    systemctl start xrdp
                    ;;
                "OpenSUSE")
                    zypper install -y xrdp
                    systemctl enable xrdp
                    systemctl start xrdp
                    ;;
                # Add other distros here...
                *)
                    echo "RDP not supported for this distribution."
                    ;;
            esac
            ;;
        "vnc")
            case $distro in
                "Ubuntu"|"Debian")
                    apt-get install -y tightvncserver
                    ;;
                "Fedora")
                    dnf install -y tigervnc-server
                    ;;
                "CentOS")
                    yum install -y tigervnc-server
                    ;;
                "Arch Linux")
                    pacman -S --noconfirm tigervnc
                    ;;
                "OpenSUSE")
                    zypper install -y tigervnc
                    ;;
                # Add other distros here...
                *)
                    echo "VNC not supported for this distribution."
                    ;;
            esac
            ;;
        "none")
            echo "No remote access tools will be installed."
            ;;
        *)
            echo "Invalid option. No remote access tools will be installed."
            ;;
    esac
}

setup_remote_access $remote_access

# Prompt for control panel installation
declare -a control_panels=("Webmin" "cPanel" "Plesk" "ISPConfig" "Ajenti" "VestaCP" "CentOS Web Panel" "Froxlor" "DirectAdmin" "CyberPanel")

echo "Do you want to install a control panel? (Choose a number or type 'none')"
select control_panel in "${control_panels[@]}" "none"; do
    case $control_panel in
        "Webmin")
            # Installation steps for Webmin
            wget -qO - http://www.webmin.com/jcameron-key.asc | apt-key add -
            echo "deb http://download.webmin.com/download/repository sarge contrib" > /etc/apt/sources.list.d/webmin.list
            apt-get update
            apt-get install -y webmin
            ;;
        "cPanel")
            # Installation steps for cPanel
            cd /home
            curl -o latest -L https://securedownloads.cpanel.net/latest
            sh latest
            ;;
        "Plesk")
            # Installation steps for Plesk
            sh <(curl http://autoinstall.plesk.com/one-click-installer)
            ;;
        "ISPConfig")
            # Installation steps for ISPConfig
            wget -O - https://get.ispconfig.org | sh
            ;;
        "Ajenti")
            # Installation steps for Ajenti
            apt-get update && apt-get install -y wget apt-transport-https
            wget http://repo.ajenti.org/debian/key -O- | apt-key add -
            echo "deb http://repo.ajenti.org/ng/debian main main ubuntu" >> /etc/apt/sources.list
            apt-get update
            apt-get install -y ajenti
            ;;
        "VestaCP")
            # Installation steps for VestaCP
            curl -O http://vestacp.com/pub/vst-install.sh
            bash vst-install.sh
            ;;
        "CentOS Web Panel")
            # Installation steps for CentOS Web Panel
            cd /usr/local/src
            wget http://centos-webpanel.com/cwp-el7-latest
            sh cwp-el7-latest
            ;;
        "Froxlor")
            # Installation steps for Froxlor
            apt-get install -y froxlor
            ;;
        "DirectAdmin")
            # Installation steps for DirectAdmin
            wget -O setup.sh https://www.directadmin.com/setup.sh
            chmod 755 setup.sh
            ./setup.sh auto
            ;;
        "CyberPanel")
            # Installation steps for CyberPanel
            sh <(curl -s https://cyberpanel.net/install.sh)
            ;;
        "none")
            echo "No control panel will be installed."
            break
            ;;
        *)
            echo "Invalid option. No control panel will be installed."
            break
            ;;
    esac
done

# Prompt for popular packages/toolkits installation
declare -a packages=("Git" "Docker" "Node.js" "Python" "Java" "Ruby" "PHP" "MySQL" "PostgreSQL" "Nginx" "Apache" "MongoDB" "Redis" "Elasticsearch" "Kubernetes")

echo "Do you want to install popular packages/toolkits? (Choose a number or type 'none')"
select package in "${packages[@]}" "none"; do
    case $package in
        "Git")
            apt-get install -y git
            ;;
        "Docker")
            apt-get install -y docker.io
            ;;
        "Node.js")
            apt-get install -y nodejs npm
            ;;
        "Python")
            apt-get install -y python3 python3-pip
            ;;
        "Java")
            apt-get install -y default-jdk
            ;;
        "Ruby")
            apt-get install -y ruby
            ;;
        "PHP")
            apt-get install -y php libapache2-mod-php
            ;;
       
