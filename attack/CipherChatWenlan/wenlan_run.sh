
for i in "Ethics_And_Morality" \
         "Inquiry_With_Unsafe_Opinion" "Insult" "Mental_Health" "Physical_Harm" \
         "Role_Play_Instruction" \
         "Unfairness_And_Discrimination" 
do
    python wenlan_main.py \
        --model_name meta-llama/Llama-3.1-70B-Instruct \
        --encode_method unchange \
        --instruction_type $i \
        # --debug_num 40
done

    
# encode_expert_dict = {
#     "unchange": BaseExpert(),
#     "baseline": BaseExpert(),
#     "caesar": CaesarExpert(),
#     "unicode": UnicodeExpert(),
#     "morse": MorseExpert(),
#     "atbash": AtbashExpert(),
#     "utf": UTF8Expert(),
#     "ascii": AsciiExpert(),
#     "gbk": GBKExpert(),
#     "selfdefine": SelfDefineCipher(),
# }

# default=["Crimes_And_Illegal_Activities", "Ethics_And_Morality",
#                                  "Inquiry_With_Unsafe_Opinion", "Insult", "Mental_Health", "Physical_Harm",
#                                  "Privacy_And_Property", "Reverse_Exposure", "Role_Play_Instruction",
#                                  "Unfairness_And_Discrimination", "Unsafe_Instruction_Topic"][0])