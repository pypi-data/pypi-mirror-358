import pandas as pd
from idvpackage.iraq_id_extraction_withopenai_test import extract_back
import openai

def fix_family_number(ocr_output):
    ocr_output = ocr_output.replace(" ","")

    if len(ocr_output)==18:
        return ocr_output
    # Step 1: Remove all non-digit characters just in case
    digits_only = ''.join(filter(str.isdigit, ocr_output))


    # Step 3: Insert 'L' at position 4 (index 4)
    before_L = digits_only[:4]
    after_L = digits_only[4:]
    fixed = before_L + 'L' + after_L

    if len(fixed)==18:
        return fixed

    # Step 4: After 'L', find where the zeros end and non-zero digits begin
    after_L_part = fixed[5:]  # characters after 'L'
    zero_count = 0

    for ch in after_L_part:
        if ch == '0':
            zero_count += 1
        else:
            break  # stop at the first non-zero digit

    # Step 5: Insert 'M' just after the zeros (before the first non-zero digit)
    insertion_index = 5 + zero_count  # 5 = index right after L
    fixed = fixed[:insertion_index] + 'M' + fixed[insertion_index:]

    return fixed


# numbers  = ['1010006650015401',
# '1004L00M8700007301',
# '10100002424835401',
# '101100M267000 1806']
# numbers = ['101100M267000 1806']
# for num in numbers:
#     print(f"Fam num before: {num}")
#     x = fix_family_number(num)
#     print(f"Fam num after: {x}")
#     print(len(x))
#     print("============================")

genai_key = "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"
openai.api_key = genai_key
df = pd.read_csv("/Users/husunshujaat/Downloads/iraq_family_number_test_batch_1.csv")

outputs = []
for ocr_text, file in zip(df['side'], df['file']):
    data = extract_back(ocr_text, openai_key=genai_key)
    print(data)
    if 'family_number' in data.keys():
        family_num = data['family_number']
        fixed_fam_num = fix_family_number(family_num)
        output = {"file":file, "family_num_before":family_num, "family_num_fixed":fixed_fam_num,"len_fam_num":len(family_num),  "len_fixed_fam_num":len(fixed_fam_num)}
        outputs.append(output)

pd.DataFrame(outputs).to_csv('/Users/husunshujaat/Downloads/fixed_fam_num.csv')
