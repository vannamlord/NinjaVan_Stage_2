install:
    auto start
    copy file to install folder on Desktop
lib:
    {
        network-manager-cli config:
        sudo apt-get install network-manager (Normally -> Already have on DWS machine)

        wifi config:
        wifi_default_name = Ninja Van
        wifi_4g = dws4g
        wifi_pass = Ninjav@nwifi!
        
        speedtest-cli config:
        sudo apt install speedtest-cli ; apt update;\
        sudo gzip -k9 /usr/lib/python3/dist-packages/speedtest.py; \
        sudo wget https://raw.githubusercontent.com/sivel/speedtest-cli/v2.1.3/speedtest.py -O /usr/lib/python3/dist-packages/speedtest.py
    }