import os
import jieba
import math
import collections

# 获取停词库
def get_stop_word(stop_word_file):
    stop_word_list = []
    with open(stop_word_file, "r", encoding="utf-8") as file_to_read:
        for line in file_to_read:
            stop_word_list.append(line.strip())
    return stop_word_list
# 获取标点符号库
def get_punctuation_word(punctuation_file):
    punctuation_list = []
    with open(punctuation_file, "r", encoding="utf-8") as file_to_read:
        for line in file_to_read:
            punctuation_list.append(line.strip())
    return punctuation_list
# 获取去除 停词、标点符号 的词表
def get_cleaned_word_list(sentence, stop_word_list, punctuation_list):
    word_list = jieba.lcut(sentence)
    cleaned_word_list = []
    for word in word_list:
        if word in stop_word_list or word in punctuation_list:
            continue
        cleaned_word_list.append(word)
    return cleaned_word_list
def get_cleaned_charater_list(sentence, stop_word_list, punctuation_list):
    cleaned_charater_list = []
    for word in sentence:
        if word in stop_word_list or word in punctuation_list:
            continue
        cleaned_charater_list.append(word)
    return cleaned_charater_list
# 获取N元语言模型
def getNmodel(phrase_model, n, words_list):
    if n == 1:
        for i in range(len(words_list)):
            phrase_model[words_list[i]] = phrase_model.get(words_list[i], 0) + 1
    else:
        for i in range(len(words_list) - (n - 1)):
            if n == 2:
                condition_t = words_list[i]
            else:
                condition = []
                for j in range(n-1):
                    condition.append(words_list[i + j])
                condition_t = tuple(condition)
            phrase_model[(condition_t, words_list[i+n-1])] = phrase_model.get((condition_t, words_list[i+n-1]), 0) + 1
    return phrase_model
# 获取N元信息熵
def getNentropy(n, clean_zh_file_content):
    if n == 1:
        phrase_model = getNmodel({}, 1, clean_zh_file_content)
        model_lenth = len(clean_zh_file_content)
        entropy = sum(
            [-(phrase[1] / model_lenth) * math.log(phrase[1] / model_lenth, 2) for phrase in phrase_model.items()])
    elif n>1:
        phrase_model_pre = getNmodel({}, n-1, clean_zh_file_content)
        phrase_model = getNmodel({}, n, clean_zh_file_content)
        phrase_n_len = sum([phrase[1] for phrase in phrase_model.items()])
        entropy = 0
        for n_phrase in phrase_model.items():
            p_xy = n_phrase[1] / phrase_n_len
            p_x_y = n_phrase[1] /  phrase_model_pre[n_phrase[0][0]]
            entropy+=(-p_xy * math.log(p_x_y, 2))
    return entropy

import matplotlib.pyplot as plt
# 画图
def draw_img(imgs_folder, zh_file_entropy, type="word"):
    x_axis = [key[:-4] for key in zh_file_entropy.keys()] # 书名为x轴
    entropy_one = [value[0] for key,value in zh_file_entropy.items()] # 信息熵为y轴
    entropy_two = [value[1] for key,value in zh_file_entropy.items()]
    entropy_three = [value[2] for key, value in zh_file_entropy.items()]
    entropy = []
    entropy.append(entropy_one)
    entropy.append(entropy_two)
    entropy.append(entropy_three)

    # 解决图片中中文乱码解决
    plt.rcParams['font.family'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
    # 遍历画图
    for index in range(len(entropy)):
        for i in range(len(x_axis)):
            plt.bar(x_axis[i], entropy[index][i], width=0.5)
        if type=="word":
            plt.title(str(index+1)+"元信息熵词分析")
        else:
            plt.title(str(index + 1) + "元信息熵字分析")
        # 设置x轴标签名
        plt.xlabel("书名")
        # 设置y轴标签名
        plt.ylabel("信息熵")
        # 显示
        plt.xticks(fontsize=7)
        plt.show()
        plt.savefig(os.path.join(imgs_folder,str(index)+".jpg"))

if __name__ == "__main__":
    zh_file_folder = "./jyxstxtqj"
    stop_word_file = "./cn_stopwords.txt"
    punctuation_file = "./cn_punctuation.txt"
    imgs_folder = "./result_img"

    # 获取所有的小说文件名
    zh_files = os.listdir(zh_file_folder)

    # 获取停词库
    stop_word_list = get_stop_word(stop_word_file)

    # 获取需要去除的标点符号
    punctuation_list = get_punctuation_word(punctuation_file)

    # 遍历每一本小说
    zh_file_word_entropy = collections.defaultdict(list) # 用来记录n元信息熵
    zh_file_charater_entropy = collections.defaultdict(list)
    for zh_file in zh_files:
        zh_file_path = os.path.join(zh_file_folder, zh_file)
        clean_zh_file_word_content = []
        clean_zh_file_charater_content = []
        with open(zh_file_path, "r", encoding="gb18030") as file_to_read:
            for line in file_to_read:
                if line.strip() == "本书来自www.cr173.com免费txt小说下载站" or line.strip() == "更多更新免费电子书请关注www.cr173.com":
                    continue
                cleaned_word_list = get_cleaned_word_list(line.strip(), stop_word_list, punctuation_list)
                cleaned_charater_list = get_cleaned_charater_list(line.strip(), stop_word_list, punctuation_list)
                # 得到去除停用词和标点符号的词列表
                clean_zh_file_word_content.extend(cleaned_word_list)
                clean_zh_file_charater_content.extend(cleaned_charater_list)
            # 计算该本小说的n元信息熵 此处：1-3元
            for i in range(1, 4):
                entropy_word = getNentropy(i, clean_zh_file_word_content)
                entropy_charater = getNentropy(i, clean_zh_file_charater_content)
                zh_file_word_entropy[zh_file].append(entropy_word) # {文件名:[entropy_1,entropy_2,...entropy_n]}
                zh_file_charater_entropy[zh_file].append(entropy_charater)
    # 输出不同小说的n元信息熵
    print(zh_file_word_entropy)
    print(zh_file_charater_entropy)
    # 画图
    draw_img(imgs_folder, zh_file_word_entropy, type="word")
    draw_img(imgs_folder, zh_file_charater_entropy, type="charater")
    print("Finish!")










