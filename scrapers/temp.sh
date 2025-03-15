docker buildx build --platform linux/amd64 --provenance=false -t dell_price_check_scrapers_lambda:latest .
docker run --platform linux/amd64 -p 9000:8080 --rm dell_price_check_scrapers_lambda:latest
docker run --platform linux/amd64 -it --rm --entrypoint /bin/sh dell_price_check_scrapers_lambda:latest

# 別のbashで
$ curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

# 初回のみ
aws ecr create-repository --repository-name dell_price_check_scrapers_lambda --region ap-northeast-1 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

docker tag dell_price_check_scrapers_lambda:latest 054037112861.dkr.ecr.ap-northeast-1.amazonaws.com/dell_price_check_scrapers_lambda:latest
docker push 054037112861.dkr.ecr.ap-northeast-1.amazonaws.com/dell_price_check_scrapers_lambda
