cmd to create kubernetes secrets: 
microk8s kubectl create secret generic buffet-secrets -n production \
  --from-literal=DATABASE_URL='postgresql://buffet_user:your_secure_password@buffet-postgres-service:5432/buffet_prod' \
  --from-literal=PAYPAL_CLIENT_ID='...' \
  --from-literal=PAYPAL_SECRET='...' \
  --from-literal=MAIL_USERNAME='...' \
  --from-literal=MAIL_PASSWORD='...' \
  --from-literal=MAIL_FROM='...' \
  --dry-run=client -o yaml | microk8s kubectl apply -f -
