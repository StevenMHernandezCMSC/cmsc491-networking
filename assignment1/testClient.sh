echo "   TEST: Loading http://google.com should show redirect uri to http://www.google.com"
python HTTPClient.py http://google.com

echo "   TEST: Loading http://egr.vcu.edu/index.html"
python HTTPClient.py http://egr.vcu.edu/index.html

echo "   TEST: Loading http://stevenhdesigns.com:80"
python HTTPClient.py http://stevenhdesigns.com:80

echo "   TEST: Loading http://stevenhdesigns.com/assets/js/bower_components/font-awesome/css/font-awesome.min.css"
python HTTPClient.py http://stevenhdesigns.com/assets/js/bower_components/font-awesome/css/font-awesome.min.css

echo "   TEST: Client should not be able to load https"
python HTTPClient.py https://google.com

echo "   TEST: Client should not be able to load https"
python HTTPClient.py http://www.cnn.com/index.html
