#!/bin/bash

echo "Creating S3 bucket for offline page..."

aws s3 mb s3://flowspace-frontend-prod --region ap-south-1

aws s3api put-bucket-ownership-controls   --bucket flowspace-frontend-prod   --ownership-controls Rules=[{ObjectOwnership=BucketOwnerPreferred}]

aws s3api put-public-access-block   --bucket flowspace-frontend-prod   --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-policy --bucket flowspace-frontend-prod --policy '{"Version":"2012-10-17","Statement":[{"Sid":"PublicReadGetObject","Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::flowspace-frontend-prod/*"}]}'

aws s3api put-bucket-website --bucket flowspace-frontend-prod --website-configuration '{"IndexDocument":{"Suffix":"index.html"},"ErrorDocument":{"Key":"index.html"}}'

aws s3 cp frontend/public/offline.html s3://flowspace-frontend-prod/index.html
aws s3 cp frontend/public/offline.html s3://flowspace-frontend-prod/offline.html

echo "Done! Offline page live at:"
echo "http://flowspace-frontend-prod.s3-website.ap-south-1.amazonaws.com"
