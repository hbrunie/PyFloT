for ((i=1; i<=$1; i++))
do
    echo $i
    sed "${i}q;d" "$2" >> ./TMP/strat${i}.txt
done
