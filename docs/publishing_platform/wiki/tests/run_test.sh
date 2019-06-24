
gedis_port=$1 
gedis_client=$2 
cred_path=$3
wikis_name=$4
docs_url=$5
domain=$6
local_ip=$7

python3 install.py -gp gedis_port -gn gedis_client -p cred_path  -wn wikis_name -dc docs_url -d domain -ip local_ip