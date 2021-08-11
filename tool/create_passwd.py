import random
import string


def generate_password(special_character=True, password_length=8):
    """
    默认创建包含大写+小写+特殊字符+数字组成的首字母大写的16位密码, True代表包含, False代表不包含.
    :param special_character: bool类型, 是否包含特殊字符
    :param password_length: int类型, 密码长度, 默认16位, 最少8位, 最多16位
    :return: password
    """
    uppercase_letter_value_list = string.ascii_uppercase
    lowercase_letter_value_list = string.ascii_lowercase
    number_value_list = string.digits
    special_character_value_list = '!@#$%^&*()_+-='

    if not isinstance(special_character, bool):
        raise TypeError('special_character parameter must be bool type')
    if not isinstance(password_length, int):
        raise TypeError('password_length parameter must be int type')

    if 8 <= password_length <= 16:
        if special_character:
            # 定义4种类型的个数, 总数为password_length
            uppercase_letter_count = random.randint(1, 2)
            special_character_count = random.randint(3, 3)
            number_count = random.randint(2, 2)
            lowercase_letter_count = password_length - (uppercase_letter_count + special_character_count + number_count)
            # 随机生成密码
            uppercase_letter_password_list = random.sample(uppercase_letter_value_list, uppercase_letter_count)
            other_password_list = (random.sample(special_character_value_list, special_character_count)
                                   + random.sample(lowercase_letter_value_list, lowercase_letter_count)
                                   + random.sample(number_value_list, number_count))
            random.shuffle(other_password_list)
            password = ''.join(uppercase_letter_password_list) + ''.join(other_password_list)
            return password
        else:
            # 定义不带特殊字符类型的个数, 总数为password_length
            uppercase_letter_count = random.randint(2, 3)
            number_count = random.randint(2, 4)
            lowercase_letter_count = password_length - (uppercase_letter_count + number_count)

            # 随机生成密码
            uppercase_letter_password_list = random.sample(uppercase_letter_value_list, uppercase_letter_count)
            other_password_list = (random.sample(lowercase_letter_value_list, lowercase_letter_count)
                                   + random.sample(number_value_list, number_count))
            random.shuffle(other_password_list)
            password = ''.join(uppercase_letter_password_list) + ''.join(other_password_list)
            return password
    else:
        raise ValueError('password_length parameter must be greater or equal to 8 or less than or equal to 16')

