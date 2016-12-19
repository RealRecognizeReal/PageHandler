# PageHandler
refine the data and send request to search engine

## worker
formulas and page source are sended using multiple threads

## refiner
delete style tags, and useless parentheses
convert ltx to mathml

## requester
send http request to engine (restful api)
get html source

## getter
make data(formula and url are included) using multiple threads

## merger (/sets)
merge outfiles and make output data(merge.out)

## matcher (/sets/data)
find 10 most similar formulas's link using output data(merge.out)

## settings (docker, python, node)
- docker
docker run -dit -p 9200:9200 -v hostsharedirectory:/usr/share/elasticsearch/data --name myname elasticsearch:2.4
docker run -dit --link my-ela:my-ela --name myname2 python:2.7
- node (6.8.1v)
- python
pip install requests pymongo Naked
