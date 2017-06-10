all:
	ssh -t janssen@web535.webfaction.com 'cd /home/janssen/webapps/new_rodolphejanssen_com/Jason-Scraper; git pull; cd ../ apache2/bin/restart'
