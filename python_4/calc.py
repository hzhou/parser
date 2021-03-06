import readline
import re
def main():
    while 1:
        line = input("> ")
        if line=="quit":
            break
        else:
            print(calc(line))

def calc(src):
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
            # r"\s+"
            m = re1.match(src, src_pos)
            if m:
                src_pos=m.end()
                continue
            # r"[\d\.]+"
            m = re2.match(src, src_pos)
            if m:
                src_pos=m.end()
                num = float(m.group(0))
                cur=( num, "num")
                break
            # r"[-+*/]"
            m = re3.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            if src_pos<src_len and src[src_pos]=='(':
                src_pos+=1
                cur = ('(', '(')
                break
            if src_pos<src_len and src[src_pos]==')':
                src_pos+=1
                cur = (')', ')')
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
                    elif stack[-1][1] in boc_type:
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
                    if stack[-2][1] == '(':
                        cur = stack[-1]
                        stack[-2:]=[]
                    elif stack[-2][1] == "unary":
                        t = -stack[-1][0]
                        stack[-2:]=[(t, "num")]
                    elif stack[-2][1]=='+':
                        t = stack[-3][0] + stack[-1][0]
                        stack[-3:]=[(t, "num")]
                    elif stack[-2][1]=='-':
                        t = stack[-3][0] - stack[-1][0]
                        stack[-3:]=[(t, "num")]
                    elif stack[-2][1]=='*':
                        t = stack[-3][0] * stack[-1][0]
                        stack[-3:]=[(t, "num")]
                    elif stack[-2][1]=='/':
                        t = stack[-3][0] / stack[-1][0]
                        stack[-3:]=[(t, "num")]
                    continue
            break
        if cur is None:
            continue
        if cur[1] == "eof":
            break
        elif cur[1]:
            stack.append(cur)
    if len(stack)!=2:
        print("stack: ", stack);
        raise Exception("unreduced parse stack")
    return stack[1]

re1 = re.compile(r"\s+")
re2 = re.compile(r"[\d\.]+")
re3 = re.compile(r"[-+*/]")
if __name__ == "__main__":
    main()
