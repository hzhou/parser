import re

variables={}

def main():
    s = """
    a=1
    1+2*3;
    !a?2:3
    """
    parse_javascript(s)

def parse_javascript(src):
    def got_statement(stmt):
        if stack[-1][0]=="if_block":
            stack.pop()
        print(stmt)

    def skip_space(skip_newline=0):
        nonlocal src_pos
        while src_pos<src_len:
            if skip_newline:
                # r"\s+"
                m = re1.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    continue
            else:
                # r"[ \t]+"
                m = re2.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    continue
            # r"//.*$", re.M
            m = re3.match(src, src_pos)
            if m:
                src_pos=m.end()
                continue
            # r"/\*.*?\*/", re.S
            m = re4.match(src, src_pos)
            if m:
                src_pos=m.end()
                continue
            break

    def match_end_of_statement():
        nonlocal src_pos
        if src[src_pos]==';':
            src_pos+=1
            skip_space(1)
            return 1
        # r"[\r\n]+"
        m = re5.match(src, src_pos)
        if m:
            src_pos=m.end()
            skip_space(1)
            if stack[-1][1] in atom_type:
                if src_pos>=src_len or re.match(r"[$\w\d_]", src[src_pos]):
                    return 1
        return 0


    precedence = {'bof':0,'eof':0,'boc':0,'(':0,')':0,';':1,',':1,':{':2,'=':2,'+=':2,'-=':2,'*=':2,'/=':2,'%=':2,'&=':2,'^=':2,'|=':2,'<<=':2,'>>=':2,'>>>=':2,'?':3,':':3,'||':4,'&&':5,'|':6,'^':7,'&':8,'==':9,'!=':9,'===':9,'!==':9,'instanceof':10,'in':10,'<':10,'<=':10,'>':10,'>=':10,'<<':11,'>>':11,'>>>':11,'+':12,'-':12,'*':13,'/':13,'%':13,'.':15,'unary':99}
    boc_type=['(', 'boc', 'bof', 'eof']
    atom_type=['']
    unary_type=[]
    right_precedences=[]
    literal_type = ["bool", "null", "int", "float", "string"]
    number_type = ["int", "float", "num"]
    float_type  = ["float"]
    expr_type   = ["identifier"]
    expr_type.extend(["binary_exp", "unary_exp", "list_exp", "++_exp", "--_exp"])
    expr_type.extend(["member", "fcall", "index"])
    atom_type.extend(literal_type)
    atom_type.extend(number_type)
    atom_type.extend(expr_type)
    is_op_unary = ["~", "!", "delete", "new", "typeof", "void"]
    unary_type.extend(["+", "-", "++", "--"])
    unary_type.extend(is_op_unary)
    right_precedences = [2,3]
    stack=[('', 'bof')]
    src_len=len(src)
    src_pos=0
    while 1:
        while 1: # $do
            if src_pos>=src_len:
                cur = ("", "eof")
                break
            if stack[-1][1] in boc_type:
                skip_space(1)
            else:
                skip_space(0)
            if src_pos>=src_len:
                continue
            if match_end_of_statement():
                cur = (';', ';')
                break
            if src_pos<src_len and src[src_pos]=='{':
                src_pos+=1
                stack.append(("compound", "boc"))
                continue
            if src_pos<src_len and src[src_pos]=='}':
                src_pos+=1
                if stack[-1][1]=="boc":
                    stack.append(("", ""))
                cur = ('}', ")")
                break
            # r"if\b"
            m = re6.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='(':
                    src_pos+=1
                    stack.append(("if_cond", "boc"))
                else:
                    print("stack: ", stack);
                    raise Exception("if missing (")
            # r"[\d\.]+"
            m = re7.match(src, src_pos)
            if m:
                src_pos=m.end()
                num = float(m.group(0))
                cur=( num, "num")
                break
            if src_pos<src_len and src[src_pos]=='(':
                src_pos+=1
                cur = ('(', '(')
                break
            if src_pos<src_len and src[src_pos]==')':
                src_pos+=1
                cur = (')', ')')
                break
            # r"\+\+|--"
            m = re8.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                if stack[-1][1] in atom_type:
                    if stack[-1][1]!= 'identifier':
                        print("stack: ", stack);
                        raise Exception("Only identifier can used with "+op)
                    if op=="++":
                        variables[stack[-1][0]] += 1
                    elif op=="--":
                        variables[stack[-1][0]] -= 1
                else:
                    stack.append((op, "unary"))
                continue
            # r"new|in|delete|typeof|void|instanceof"
            m = re9.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"(==?=?|!==?|>>?>?=?|<<?=?|&&?|\|\|?)"
            m = re10.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"[+\-*/%^&|]=?"
            m = re11.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"[,~!\?:]"
            m = re12.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"[a-zA-Z_\$]\w*"
            m = re13.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur = (m.group(0), "identifier")
                break
            src_pos+=1
            continue
            break
        while 1: # $do
            if cur[1] in atom_type:
                if stack[-1][1] in atom_type:
                    print("cur: ", cur)
                    print("stack: ", stack);
                    raise Exception("two adjacent atoms")
            else:
                if stack[-1][1] not in atom_type:
                    if cur[1] in unary_type:
                        cur=(cur[0], "unary")
                        break
                    elif cur[1] in boc_type:
                        break
                    else:
                        print("cur: ", cur, "last type: ", stack[-1][1])
                        print("stack: ", stack);
                        raise Exception("operator in wrong context")
                if len(stack)<=1:
                    break
                if precedence[cur[1]]<precedence[stack[-2][1]] or precedence[cur[1]]==precedence[stack[-2][1]] and precedence[cur[1]] not in right_precedences:
                    if stack[-2][1]=='bof':
                        break
                    if stack[-2][1] == 'boc':
                        cur = None
                        if stack[-2][0]=="compound":
                            got_statement(stack[-1])
                        if stack[-2][0]=="if_cond":
                            cur = ("if_block", "boc")
                        stack[-2:] = []
                        break
                    elif stack[-2][1] == '(':
                        cur = stack[-1]
                        stack[-2:]=[]
                        break
                    elif stack[-2][1] == "unary":
                        t = unary_op(stack[-2][0], stack[-1])
                        stack[-2:]=[(t, "num")]
                    elif stack[-2][1] == ':':
                        if len(stack)>5 and stack[-4][1]=='?':
                            t = get_token_value(stack[-5])
                            if t:
                                stack[-5:]=[stack[-3]]
                            else:
                                stack[-5:]=[stack[-1]]
                        else:
                            print("stack: ", stack);
                            raise Exception("Ternary operators have been messed up.")
                    elif precedence[stack[-2][1]]==2 and stack[-2][1][-1]=='=':
                        if stack[-3][1]!= 'identifier':
                            print("stack: ", stack);
                            raise Exception("Only identifier can be on the left side of assignment!")
                        if stack[-2][1]=='=':
                            t = get_token_value(stack[-1])
                        else:
                            op = stack[-2][1][:-1]
                            t = binary_op(op, stack[-3], stack[-1])
                        variables[stack[-3][0]] = t
                        stack[-3:]=[(t, 'num')]
                    else:
                        t = binary_op(stack[-2][1], stack[-3], stack[-1])
                        stack[-3:]=[(t, "num")]
                    continue
            break
        if cur is None:
            continue
        if cur[1] == ';':
            stmt = stack.pop()
            got_statement(stmt)
            continue
        if cur[1] == "eof":
            break
        elif cur[1]:
            stack.append(cur)
    return

def get_token_value(var):
    if var[1]=="identifier":
        if var[0] in variables:
            return variables[var[0]]
        else:
            print("stack: ", stack);
            raise Exception("variable "+var[0]+" not defined!")
    else:
        return var[0]

def unary_op(op, token):
    t = get_token_value(token)
    if op =='-':
        return -t
    elif op =='!':
        return not t
    elif op =='~':
        return ~int(t)
    if op =='++' or op == '--':
        if token[1] != "identifier":
            print("stack: ", stack);
            raise Exception(op+" on non-variable!")
        if op=='++':
            t+=1
        else:
            t-=1
        variables[token[0]]=t
        return t
    else:
        print("stack: ", stack);
        raise Exception("unary operator "+op+" not supported!")

def binary_op(op, a, b):
    t_a = get_token_value(a)
    t_b = get_token_value(b)
    if 0:
        pass
    elif op =='+':
        return t_a + t_b
    elif op =='-':
        return t_a - t_b
    elif op =='*':
        return t_a * t_b
    elif op =='/':
        return t_a / t_b
    elif op =='%':
        return int(t_a) % int(t_b)
    elif op =='<<':
        return int(t_a) << int(t_b)
    elif op =='>>':
        return int(t_a) >> int(t_b)
    elif op =='^':
        return int(t_a) ^ int(t_b)
    elif op =='&':
        return int(t_a) & int(t_b)
    elif op =='|':
        return int(t_a) | int(t_b)
    elif op =='&&':
        return t_a and t_b
    elif op =='||':
        return t_a or t_b
    else:
        print("stack: ", stack);
        raise Exception("unhandled operator ["+op+"]")

re1 = re.compile(r"\s+")
re2 = re.compile(r"[ \t]+")
re3 = re.compile(r"//.*$", re.M)
re4 = re.compile(r"/\*.*?\*/", re.S)
re5 = re.compile(r"[\r\n]+")
re6 = re.compile(r"if\b")
re7 = re.compile(r"[\d\.]+")
re8 = re.compile(r"\+\+|--")
re9 = re.compile(r"new|in|delete|typeof|void|instanceof")
re10 = re.compile(r"(==?=?|!==?|>>?>?=?|<<?=?|&&?|\|\|?)")
re11 = re.compile(r"[+\-*/%^&|]=?")
re12 = re.compile(r"[,~!\?:]")
re13 = re.compile(r"[a-zA-Z_\$]\w*")
if __name__ == "__main__":
    main()
