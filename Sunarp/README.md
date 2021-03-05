Installing dependencies
=======================

ImageMafic Tools:

```
$ sudo apt-get install imagemagick-6.q16
```

Redis:

```
$ sudo apt-get install redis-server
```

Tesseract OCR:

    1  nano ~/.ssh/authorized_keys 
    2  ls
    3  sudo apt-get install python-dev python-pip git docker.io
    4  docker ps
    5  sudo usermod -a -G docker $USER
    6  docker ps
    7  sudo reboot 
    8  python
    9  sudo apt-get install git
   10  sudo apt install zlib1g-dev libffi-dev
   11  sudo apt-get update 
   12  sudo apt install zlib1g-dev libffi-dev
   13  sudo apt install libssl-dev
   14  sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
   15  wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz
   16  tar -xf Python-3.7.3.tar.xz
   17  ls
   18  cd Python-3.7.3/
   19  ls
   20  ./configure --enable-optimizations
   21  make
   22  ls
   23  docker ps
   24  rm Python-3.7.3
   25  python
   26  rm -rf Python-3.7.3*
   27  ls
   28  ls -l
   29  python3
   30  git
   31  ls
   32  pwd
   33  sudo apt-get install tesseract-ocr tesseract-ocr-spa libtesseract-dev
   34  sudo apt-get install python3-dev 
   35  sudo apt-get install python3-dev python3-setuptools
   36  sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev     libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev     tcl8.6-dev tk8.6-dev python-tk
   37  du -h
   38  rq --help
   39  cd sunarp-scrapping/
   40  source venv/bin/activate
   41  rq --hel
   42  rq --help
   43  cd /etc/supervisor/conf.d/
   44  sudo touch manar.conf
   45  sudo nano manar.conf 
   46  sudo supervisorctl update
   47  sudo supervisorctl reread
   48  sudo supervisorctl start all
   49  sudo supervisorctl status
   50  tail -f /var/log/sunar-queue.log 
   51  sudo nano manar.conf 
   52  sudo supervisorctl restart
   53  sudo supervisorctl restart all
   54  sudo supervisorctl status
   55  tail -f /var/log/sunar-queue.log 
   56  sudo nano  manar.conf manar.conf 
   57  sudo nano  manar.conf 
   58  sudo supervisorctl restart all
   59  sudo supervisorctl reread
   60  sudo supervisorctl update
   61  sudo supervisorctl restart all
   62  sudo supervisorctl status
   63  sudo supervisorctl restart all
   64  sudo supervisorctl logs all
   65  sudo supervisorctl log all
   66  sudo supervisorctl --help
   67  sudo supervisorctl help
   68  sudo supervisorctl tail all
   69  sudo supervisorctl tail sunarp-queue
   70  sudo supervisorctl start all
   71  ls
   72  sudo nano manar.conf 
   73  sudo supervisorctl reread
   74  sudo supervisorctl update
   75  sudo supervisorctl restart all
   76  sudo supervisorctl tail sunart-queue
   77  sudo supervisorctl tail sunarp-queue
   78  tail -f /var/log/sunar-queue.log 
   79  sudo nano manar.conf 
   80  sudo supervisorctl reread
   81  sudo supervisorctl update
   82  sudo supervisorctl restart all
   83  tail -f /var/log/sunar-queue.log 
   84  sudo supervisorctl restart all
   85  tail -f /var/log/sunar-queue.log 
   86  ls
   87  git clone https://cesarbustios@bitbucket.org/cesarbustios/sunarp-scrapping.git
   88  cd sunarp-scrapping/
   89  ls
   90  docker build -t sunarp_app .
   91  ls
   92  cd 
   93  ls
   94  cd sunarp-scrapping/
   95  source venv/bin/activate
   96  pip freeze
   97  python app/main.py 
   98  ls
   99  python app/main.py 
  100  ls
  101  ls app/jobs/
  102  ls
  103  wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
  104  echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
  105  sudo apt-get update 
  106  sudo apt-get install google-chrome-stable
  107  sudo apt-get install supervisor
  108  supervisorctl status
  109  sudo supervisorctl status
  110  ls /etc/supervisor/conf.d/
  111  python app/main.py 
  112  google-chrome --version
  113  ls
  114  git pull --all
  115  ls
  116  python app/main.py 
  117  ls
  118  cd app/
  119  ls
  120  mkdir -p static/plates
  121  ls
  122  ls static/
  123  python app/main.py 
  124  cd ../
  125  python app/main.py 
  126  git pull --all
  127  python app/main.py 
  128  sudo apt-get install tesseract-ocr tesseract-ocr-spa libtesseract-dev
  129  tesseract --version
  130  sudo apt-get purge tesseract-ocr
  131  tesseract --version
  132  cd ../
  133  ls
  134  wget http://www.leptonica.com/source/leptonica-1.78.0.tar.gz
  135  ls
  136  tar -xf leptonica-1.78.0.tar.gz 
  137  cd leptonica-1.78.0/
  138  ./configure 
  139  sudo make
  140  sudo make install
  141  c ../
  142  cd ../
  143  wget https://github.com/tesseract-ocr/tesseract/archive/3.05.02.zip
  144  ls
  145  unzip 3.05.02.zip 
  146  sudo apt-get install unzip
  147  unzip 3.05.02.zip 
  148  ls
  149  cd tesseract-3.05.02/
  150  ls
  151  ./autogen.sh
  152  sudo apt-get install autoconf automake libtool
  153  sudo apt-get install autoconf-archive
  154  sudo apt-get install pkg-config
  155  sudo apt-get install libpng12-dev
  156  sudo apt-get install libjpeg8-dev
  157  sudo apt-get install libtiff5-dev
  158  ./autogen.sh
  159  ./configure --enable-debug
  160  ./configure --enable-debug LDFLAGS="-L/usr/local/lib" CFLAGS="-I/usr/local/include" make
  161  ./configure --enable-debug LDFLAGS="-L/usr/local/lib" CFLAGS="-I/usr/local/include"
  162  make
  163  sudo make install
  164  sudo make install-langs
  165  sudo ldconfig
  166  cd ../
  167  ls
  168  tesseract --version
  169  python app/main.py 
  170  cd sunarp-scrapping/
  171  python app/main.py 
  172  ls /usr/local/bin/tesseract 
  173  ls /usr/share/tesseract-ocr/4.00/
  174  ls /usr/share/tesseract-ocr/4.00/tessdata/
  175  cd ../
  176  ls
  177  cd tesseract-3.05.02/
  178  ls
  179  sudo make install-langs
  180  sudo apt-get install tesseract-ocr-spa
  181  ls
  182  ls /usr/local/share/tessdata/
  183  cd .
  184  cd
  185  ls
  186  wget https://github.com/tesseract-ocr/tessdata/archive/3.04.00.zip
  187  ls
  188  unzip 3.04.00.zip 
  189  ls /usr/share/tesseract-ocr/tessdata
  190  ls
  191  cd tessdata-3.04.00/
  192  ls
  193  ls /usr/local/share/tessdata
  194  ls -la /usr/local/share/tessdata
  195  sudo cp * /usr/local/share/tessdata/
  196  ls -la /usr/local/share/tessdata
  197  cd ../
  198  ls
  199  rm *.zip
  200  rm *.tar.gz

