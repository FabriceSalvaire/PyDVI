for i in *.py; do echo $i; cat $i | grep -v -E '^$' | wc -l; done
