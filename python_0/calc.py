import re
def main():
    print(calc("1+2*-3"))

def calc(src):
    src_len=len(src)
    src_pos=0
    precedence = {'eof':0, '+':1, '-':1, '*':2, '/':2, 'unary': 99}
    re1 = re.compile(r"\s+")
    re2 = re.compile(r"[\d\.]+")
    re3 = re.compile(r"[-+*/]")
    stack=[]
    while 1:
        while 1: # $do
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
            if src_len>=src_pos:
                cur = ('', "eof")
                break
            t=src[0:src_len]+" - "+src[src_len:]
            raise Exception(t)
            break
        while 1: # $do
            if cur[1]=="num":
                break
            if len(stack)<1 or stack[-1][1]!="num":
                cur = (cur[0], 'unary')
                break
            if len(stack)<2:
                break
            if precedence[cur[1]]<=precedence[stack[-2][1]]:
                if stack[-2][1] == "unary":
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
        if cur[1]!="eof":
            stack.append(cur)
        else:
            if len(stack)>0:
                return stack[-1][0]
            else:
                return None

if __name__ == "__main__":
    main()
