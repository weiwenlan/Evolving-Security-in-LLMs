
for i in "Ethics_And_Morality" \
         "Inquiry_With_Unsafe_Opinion" "Insult" "Mental_Health" "Physical_Harm" \
         "Role_Play_Instruction" \
         "Unfairness_And_Discrimination" 
do
    python wenlan_main.py \
        --model_name vicuna-7b-v1.1 \
        --encode_method unchange \
        --instruction_type $i \
        --debug_num 40
done
