import re

prime_type=["int","float","string","bool","null"]

def main():
    s = """
    a=1
    1+2*3;
    !a?2:3
    """
    print(parse_javascript(s))

def parse_javascript(src):
    def got_statement(stmt):
        nonlocal src_pos, cur_context
        if "statements" in cur_context:
            cur_context['statements'].append(stmt)
        elif cur_context["expect"]!=';':
            print_stack(stack)
            print("cur: ", cur)
            (s0, s1)=synopsis(src, 40, src_pos, src_len)
            print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
            raise Exception("Context mismatch, not expecting statement")
        else:
            t_context = stack[-1][0]
            stack.pop()
            last_context= cur_context
            cur_context = context_stack.pop()
            if 0:
                pass
            elif t_context =="if_block":
                t = (last_context["condition"], stmt)
                last_context["branch_list"].append(t)
                # r"else\b"
                m = re1.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    # r"if\b"
                    m = re2.match(src, src_pos)
                    if m:
                        src_pos=m.end()
                        skip_space(1)
                        if src_pos<src_len and src[src_pos]=='(':
                            src_pos+=1
                            context_stack.append(cur_context)
                            cur_context = last_context
                            cur_context["type"]   = "if_cond"
                            cur_context["expect"] = ")"
                            stack.append(("if_cond", "boc"))
                        else:
                            print_stack(stack)
                            print("cur: ", cur)
                            (s0, s1)=synopsis(src, 40, src_pos, src_len)
                            print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                            raise Exception("if missing (")
                    else:
                        context_stack.append(cur_context)
                        cur_context = last_context
                        cur_context["type"]   = "if_block"
                        cur_context["expect"] = ";"
                        stack.append(("if_block", "boc"))
                        cur_context["condition"]=None
                else:
                    stmt = (last_context["branch_list"], "if")
                    got_statement(stmt)
            elif t_context == "while_block":
                stmt = ( (last_context["condition"], stmt), "while")
                got_statement(stmt)
            elif t_context == "do_block":
                # r"while\b"
                m = re3.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]=='(':
                        src_pos+=1
                        last_context["block"]=stmt
                        context_stack.append(cur_context)
                        cur_context = last_context
                        cur_context["type"]   = "do_cond"
                        cur_context["expect"] = ")"
                        stack.append(("do_cond", "boc"))
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("while missing (")
                else:
                    print_stack(stack)
                    print("cur: ", cur)
                    (s0, s1)=synopsis(src, 40, src_pos, src_len)
                    print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                    raise Exception("do missing while")
            elif t_context == "for_block":
                stmt = ( (last_context["condition"], stmt), "for")
                got_statement(stmt)
            elif t_context == "with_block":
                stmt = ( (last_context["condition"], stmt), "with")
                got_statement(stmt)
            elif t_context == "switch_block":
                stmt = ( (last_context["condition"], stmt), "switch")
                got_statement(stmt)
            elif t_context == "var":
                stmt = (stmt, "var")
                got_statement(stmt)
            elif t_context == "return":
                stmt = (stmt, last_context["name"])
                got_statement(stmt)
            elif t_context=="case":
                stmt = (stmt, "case")
                got_statement(stmt)
            elif t_context == "label":
                t = (last_context["label"], stmt)
                stmt = (t, "labelled_statement")
                got_statement(stmt)

    def synopsis(s, N, i, n):
        i0=i-N
        i1=i+N
        t_pre="..."
        t_post="..."
        if i0<0:
            i0=0
            t_pre=""
        if i1>n:
            i1=n
            t_post=""
        return (t_pre+s[i0:i], s[i:i1]+t_post)

    def less_precedence(op1, op2):
        p1 = precedence[op1]
        p2 = precedence[op2]
        if op1 == '?':
            return p2 > 3
        else:
            if p1 == p2:
                if op2=='?':
                    return 0
                elif op1==':':
                    return 1
                elif p2==2:
                    return 0
                else:
                    return 1
            else:
                return p1 < p2

    def skip_space(skip_newline=0):
        nonlocal src_pos
        while src_pos<src_len:
            if skip_newline:
                # r"\s+"
                m = re4.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    continue
            else:
                # r"[ \t]+"
                m = re5.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    continue
            # r"//.*$", re.M
            m = re6.match(src, src_pos)
            if m:
                src_pos=m.end()
                continue
            # r"/\*.*?\*/", re.S
            m = re7.match(src, src_pos)
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
        m = re8.match(src, src_pos)
        if m:
            src_pos=m.end()
            skip_space(1)
            if stack[-1][1] in atom_type:
                if src_pos>=src_len or re.match(r"[$\w\d_]", src[src_pos]):
                    return 1
        return 0


    precedence = {'boc':0,'(':0,')':0,';':1,',':1,'=':2,'+=':2,'-=':2,'*=':2,'/=':2,'%=':2,'&=':2,'^=':2,'|=':2,'<<=':2,'>>=':2,'>>>=':2,'?':2,':':2,'||':4,'&&':5,'|':6,'^':7,'&':8,'==':9,'!=':9,'===':9,'!==':9,'instanceof':10,'in':10,'<':10,'<=':10,'>':10,'>=':10,'<<':11,'>>':11,'>>>':11,'+':12,'-':12,'*':13,'/':13,'%':13,'.':15,'unary':99}
    boc_type=['(', 'boc']
    atom_type=['']
    unary_type=[]
    non_stmt_boc = ["fcall", "index", "object", "array"]
    non_stmt_boc.extend(["if_cond", "while_cond", "switch_cond", "with_cond", "catch_cond", "function_param"])
    context_stack = []
    cur_context = {'type':"global", 'statements':[]}
    last_context= None
    literal_type = ["bool", "null", "int", "float", "string", "regex"]
    float_type  = ["float"]
    number_type = ["int", "float", "num"]
    compound_type = ["array", "object", "function"]
    expr_type   = ["identifier"]
    expr_type.extend(["binary_exp", "unary_exp", "list_exp", "postfix_exp", "conditional_exp"])
    expr_type.extend(["member", "fcall", "index"])
    atom_type.extend(literal_type)
    atom_type.extend(number_type)
    atom_type.extend(compound_type)
    atom_type.extend(expr_type)
    atom_type.append("object_item")
    is_op_unary = ["~", "!", "delete", "new", "typeof", "void"]
    unary_type.extend(["+", "-", "++", "--"])
    unary_type.extend(is_op_unary)
    right_precedences = [2,3]
    stack=[('global', 'boc')]
    src_len=len(src)
    src_pos=0
    while 1:
        while 1: # $do
            if src_pos>=src_len:
                cur = ("eof", ")")
                if stack[-1][1]=="boc":
                    stack.append(("", ""))
                break
            if stack[-1][1] in boc_type:
                skip_space(1)
            else:
                skip_space(0)
            if src_pos>=src_len:
                continue
            if match_end_of_statement():
                cur = (';', ';')
                if stack[-1][1]=="boc":
                    stack.append(('', ''))
                break
            if stack[-1][1] == 'boc' and stack[-1][0] not in non_stmt_boc:
                if src_pos<src_len and src[src_pos]=='{':
                    src_pos+=1
                    context_stack.append(cur_context)
                    cur_context = {"type":"compound", "expect":"}"}
                    stack.append(("compound", "boc"))
                    cur_context["statements"]=[]
                    continue
                # r"if\b"
                m = re2.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]=='(':
                        src_pos+=1
                        context_stack.append(cur_context)
                        cur_context = {"type":"if_cond", "expect":")"}
                        stack.append(("if_cond", "boc"))
                        cur_context["branch_list"]=[]
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("if missing (")
                    continue
                # r"while\b"
                m = re3.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]=='(':
                        src_pos+=1
                        context_stack.append(cur_context)
                        cur_context = {"type":"while_cond", "expect":")"}
                        stack.append(("while_cond", "boc"))
                        continue
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("while missing (")
                # r"do\b"
                m = re9.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    context_stack.append(cur_context)
                    cur_context = {"type":"do_block", "expect":";"}
                    stack.append(("do_block", "boc"))
                    continue
                # r"for\b"
                m = re10.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]=='(':
                        src_pos+=1
                        context_stack.append(cur_context)
                        cur_context = {"type":"for_cond", "expect":")"}
                        stack.append(("for_cond", "boc"))
                        cur_context["statements"]=[]
                        continue
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("for missing (")
                # r"with\b"
                m = re11.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]=='(':
                        src_pos+=1
                        context_stack.append(cur_context)
                        cur_context = {"type":"with_cond", "expect":")"}
                        stack.append(("with_cond", "boc"))
                        continue
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("with missing (")
                # r"switch\b"
                m = re12.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]=='(':
                        src_pos+=1
                        context_stack.append(cur_context)
                        cur_context = {"type":"switch_cond", "expect":")"}
                        stack.append(("switch_cond", "boc"))
                        continue
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("switch missing (")
                # r"try\b"
                m = re13.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]=='{':
                        src_pos+=1
                        context_stack.append(cur_context)
                        cur_context = {"type":"try_block", "expect":"}"}
                        stack.append(("try_block", "boc"))
                        cur_context["statements"]=[]
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("try missing {")
                    continue
                # r"var\b"
                m = re14.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    context_stack.append(cur_context)
                    cur_context = {"type":"var", "expect":";"}
                    stack.append(("var", "boc"))
                    continue
                # r"(return|throw|break|continue)\b"
                m = re15.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    context_stack.append(cur_context)
                    cur_context = {"type":"return", "expect":";"}
                    stack.append(("return", "boc"))
                    cur_context["name"]=m.group(1)
                    cur_context["expect_;"]=1
                    continue
                # r"default\b"
                m = re16.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]==':':
                        src_pos+=1
                        stmt = (None, "case")
                        got_statement(stmt)
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("default label missing :")
                    continue
                # r"case\b"
                m = re17.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    context_stack.append(cur_context)
                    cur_context = {"type":"case", "expect":";"}
                    stack.append(("case", "boc"))
                    continue
                # r"([a-zA-Z_\$]\w*):"
                m = re18.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    context_stack.append(cur_context)
                    cur_context = {"type":"label", "expect":";"}
                    stack.append(("label", "boc"))
                    cur_context["label"]=m.group(1)
                    continue
            if stack[-1][1] not in atom_type:
                # r"true|false"
                m = re19.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    cur = (m.group(0), "bool")
                    break
                # r"null\b"
                m = re20.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    cur = (m.group(0), "null")
                    break
                # r"\"(([^\\\"]|\\.)*)\""
                m = re21.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    s=js_double_string(m.group(1))
                    cur = (s, "string")
                    break
                # r"'(([^\\']|\\.)*)'"
                m = re22.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    s=js_single_string(m.group(1))
                    cur = (s, "string")
                    break
                # r"/([^\\/]|\\.)+/[igm]*"
                m = re23.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    cur = (m.group(0), "regex")
                    break
                # r"0x[0-9a-f]+", re.I
                m = re24.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    cur = (int(m.group(0), 16), "int")
                    break
                # r"0[0-7]*", re.I
                m = re25.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    cur = (int(m.group(0), 8), "int")
                    break
                # r"(\d+)(\.\d+)?([eE][+-]?\d+)?"
                m = re26.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    if m.group(2) or m.group(3):
                        cur = (float(m.group(0)), "float")
                    else:
                        cur = (int(m.group(1)), "int")
                    break
            # r"[\[\(\{]"
            m = re27.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                if stack[-1][1] in atom_type:
                    if op == '(':
                        context_stack.append(cur_context)
                        cur_context = {"type":"fcall", "expect":")"}
                        stack.append(("fcall", "boc"))
                    elif op== '[':
                        context_stack.append(cur_context)
                        cur_context = {"type":"index", "expect":"]"}
                        stack.append(("index", "boc"))
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("error opening bracket '"+op+"', forgot ';'?")
                else:
                    if op == '{':
                        context_stack.append(cur_context)
                        cur_context = {"type":"object", "expect":"}"}
                        stack.append(("object", "boc"))
                    elif op == '[':
                        context_stack.append(cur_context)
                        cur_context = {"type":"array", "expect":"]"}
                        stack.append(("array", "boc"))
                    else:
                        stack.append(('(', '('))
                continue
            # r"[\]\)\}]"
            m = re28.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, ')')
                if stack[-1][1]=='(' or stack[-1][1]=="boc":
                    stack.append(('', ''))
                break
            if src_pos<src_len and src[src_pos]==':':
                src_pos+=1
                cur = (":", ":")
                if cur_context["type"]=="case" and not stack[-2][1]=="?":
                    cur = (';', ';')
                break
            # r"\+\+|--"
            m = re29.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                if stack[-1][1] in atom_type:
                    stack[-1] = ( (op, stack[-1]), "postfix_exp")
                else:
                    stack.append((op, "unary"))
                continue
            # r"\.[a-zA-Z_\$]\w*"
            m = re30.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                if stack[-1][1] in atom_type:
                    stack[-1] = ( (op, stack[-1]), "postfix_exp")
                else:
                    print_stack(stack)
                    print("cur: ", cur)
                    (s0, s1)=synopsis(src, 40, src_pos, src_len)
                    print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                    raise Exception("member not following atom")
                continue
            # r"(new|in|delete|typeof|void|instanceof)\b"
            m = re31.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"(==?=?|!==?|>>?>?=?|<<?=?|&&?|\|\|?)"
            m = re32.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"[+\-*/%^&|]=?"
            m = re33.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"[,~!\?]"
            m = re34.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"function\b"
            m = re35.match(src, src_pos)
            if m:
                src_pos=m.end()
                statement_context=0
                if stack[-1][1] == 'boc' and stack[-1][0] not in non_stmt_boc:
                    statement_context=1
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='(':
                    src_pos+=1
                    context_stack.append(cur_context)
                    cur_context = {"type":"function_param", "expect":")"}
                    stack.append(("function_param", "boc"))
                    continue
                # r"[a-zA-Z_\$]\w*"
                m = re36.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    name = m.group(0)
                    skip_space(1)
                    if src_pos<src_len and src[src_pos]=='(':
                        src_pos+=1
                        context_stack.append(cur_context)
                        cur_context = {"type":"function_param", "expect":")"}
                        stack.append(("function_param", "boc"))
                        cur_context["name"]=name
                        if statement_context:
                            cur_context["declaration"]=1
                        continue
                    else:
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("function missing (parameters)")
            # r"[a-zA-Z_\$]\w*"
            m = re36.match(src, src_pos)
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
                    print_stack(stack)
                    print("cur: ", cur)
                    (s0, s1)=synopsis(src, 40, src_pos, src_len)
                    print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
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
                        print_stack(stack)
                        print("cur: ", cur)
                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                        raise Exception("operator in wrong context")
                if len(stack)<=1:
                    break
                if less_precedence(cur[1], stack[-2][1]):
                    if len(stack)==2:
                        break
                    if stack[-2][1] == 'boc':
                        if cur_context['expect']==cur[0]:
                            t_op      = cur
                            t_context = stack[-2][0]
                            t_atom    = stack[-1]
                            cur = None
                            stack[-2:]=[]
                            last_context= cur_context
                            cur_context = context_stack.pop()
                            if 0:
                                pass
                            elif t_context == "fcall":
                                stack[-1]=( (stack[-1], t_atom), "fcall")
                            elif t_context == "index":
                                stack[-1]=( (stack[-1], t_atom), "index")
                            elif t_context == "array":
                                if t_atom[1]=="":
                                    t_atom=[]
                                cur = (t_atom, "array")
                            elif t_context == "object":
                                cur = (t_atom, "object")
                            elif t_context =="compound":
                                last_context["statements"].append(t_atom)
                                stmt = (last_context["statements"], "compound")
                                got_statement(stmt)
                            elif t_context =="if_cond":
                                context_stack.append(cur_context)
                                cur_context = last_context
                                cur_context["type"]   = "if_block"
                                cur_context["expect"] = ";"
                                stack.append(("if_block", "boc"))
                                cur_context["condition"]=t_atom
                            elif t_context == "while_cond":
                                context_stack.append(cur_context)
                                cur_context = last_context
                                cur_context["type"]   = "while_block"
                                cur_context["expect"] = ";"
                                stack.append(("while_block", "boc"))
                                cur_context["condition"]=t_atom
                            elif t_context == "do_cond":
                                stmt = ( (t_atom, last_context["block"]), "do_while")
                                skip_space(0)
                                # r"[;\r\n]+"
                                m = re37.match(src, src_pos)
                                if m:
                                    src_pos=m.end()
                                    got_statement(stmt)
                                elif src[src_pos]=='}':
                                    got_statement(stmt)
                                else:
                                    print_stack(stack)
                                    print("cur: ", cur)
                                    (s0, s1)=synopsis(src, 40, src_pos, src_len)
                                    print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                                    raise Exception("unterminated do-while statement")
                            elif t_context == "for_cond":
                                context_stack.append(cur_context)
                                cur_context = last_context
                                cur_context["type"]   = "for_block"
                                cur_context["expect"] = ";"
                                stack.append(("for_block", "boc"))
                                t_cond_list = cur_context["statements"]
                                t_cond_list.append(t_atom)
                                cur_context["condition"]=t_cond_list
                                del cur_context["statements"]
                            elif t_context == "with_cond":
                                context_stack.append(cur_context)
                                cur_context = last_context
                                cur_context["type"]   = "with_block"
                                cur_context["expect"] = ";"
                                stack.append(("with_block", "boc"))
                                cur_context["condition"]=t_atom
                            elif t_context == "switch_cond":
                                context_stack.append(cur_context)
                                cur_context = last_context
                                cur_context["type"]   = "switch_block"
                                cur_context["expect"] = ";"
                                stack.append(("switch_block", "boc"))
                                cur_context["condition"]=t_atom
                            elif t_context =="try_block":
                                last_context["statements"].append(t_atom)
                                last_context["try_block"]=last_context["statements"]
                                del last_context["statements"]
                                last_context["catch_cond"]=None
                                last_context["catch_block"]=None
                                last_context["finally_block"]=None
                                # r"catch\b"
                                m = re38.match(src, src_pos)
                                if m:
                                    src_pos=m.end()
                                    skip_space(1)
                                    if src_pos<src_len and src[src_pos]=='(':
                                        src_pos+=1
                                        context_stack.append(cur_context)
                                        cur_context = last_context
                                        cur_context["type"]   = "catch_cond"
                                        cur_context["expect"] = ")"
                                        stack.append(("catch_cond", "boc"))
                                    else:
                                        print_stack(stack)
                                        print("cur: ", cur)
                                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                                        raise Exception("catch missing (")
                                else:
                                    stmt = ( last_context, "try")
                                    got_statement(stmt)
                            elif t_context == "catch_cond":
                                last_context["catch_cond"] = t_atom
                                if src_pos<src_len and src[src_pos]=='{':
                                    src_pos+=1
                                    context_stack.append(cur_context)
                                    cur_context = last_context
                                    cur_context["type"]   = "catch_block"
                                    cur_context["expect"] = "}"
                                    stack.append(("catch_block", "boc"))
                                    cur_context["statements"]=[]
                                else:
                                    print_stack(stack)
                                    print("cur: ", cur)
                                    (s0, s1)=synopsis(src, 40, src_pos, src_len)
                                    print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                                    raise Exception("catch missing {")
                            elif t_context == "catch_block":
                                last_context["statements"].append(t_atom)
                                last_context["catch_block"]=last_context["statements"]
                                del last_context["statements"]
                                # r"finally\b"
                                m = re39.match(src, src_pos)
                                if m:
                                    src_pos=m.end()
                                    skip_space(1)
                                    if src_pos<src_len and src[src_pos]=='{':
                                        src_pos+=1
                                        context_stack.append(cur_context)
                                        cur_context = last_context
                                        cur_context["type"]   = "finally_block"
                                        cur_context["expect"] = "}"
                                        stack.append(("finally_block", "boc"))
                                        cur_context["statements"]=[]
                                    else:
                                        print_stack(stack)
                                        print("cur: ", cur)
                                        (s0, s1)=synopsis(src, 40, src_pos, src_len)
                                        print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                                        raise Exception("finally missing {")
                                else:
                                    stmt = ( last_context, "try")
                                    got_statement(stmt)
                            elif t_context == "finally_block":
                                last_context["statements"].append(t_atom)
                                last_context["finally_block"]=last_context["statements"]
                                del last_context["statements"]
                                stmt = ( last_context, "try")
                                got_statement(stmt)
                            elif t_context=="function_param":
                                last_context["param"]=t_atom
                                skip_space(1)
                                if src_pos<src_len and src[src_pos]=='{':
                                    src_pos+=1
                                    context_stack.append(cur_context)
                                    cur_context = last_context
                                    cur_context["type"]   = "function_block"
                                    cur_context["expect"] = "}"
                                    stack.append(("function_block", "boc"))
                                    cur_context["statements"]=[]
                                else:
                                    print_stack(stack)
                                    print("cur: ", cur)
                                    (s0, s1)=synopsis(src, 40, src_pos, src_len)
                                    print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                                    raise Exception("function missing {")
                            elif t_context == "function_block":
                                last_context["statements"].append(t_atom)
                                if "declaration" in last_context:
                                    stmt = (last_context, "function")
                                    got_statement(stmt)
                                else:
                                    cur = (last_context, "function")
                        elif cur_context['expect']==';':
                            src_pos-=1
                            cur=(';', ';')
                        else:
                            print_stack(stack)
                            print("cur: ", cur)
                            (s0, s1)=synopsis(src, 40, src_pos, src_len)
                            print("source[", src_pos, "]: \"", s0, "\" + \"", s1, "\"");
                            raise Exception("Brackets mismatch, expect "+cur_context['expect']+", got "+cur[0])
                        break
                    elif stack[-2][1] == '(':
                        cur = stack[-1]
                        stack[-2:]=[]
                        break
                    elif stack[-2][1]==':' and cur_context["type"]=="object" and (stack[-4][1]==',' or stack[-4][1]=="boc"):
                        t_name = stack[-3][0]
                        t = ( (t_name, stack[-1]), "object_item")
                        stack[-3:]=[t]
                    elif stack[-2][1] == ',':
                        t=stack[-3]
                        if t[1]=="list_exp":
                            t[0].append( stack[-1] )
                        else:
                            t = ( [stack[-3], stack[-1]], "list_exp")
                        stack[-3:]=[t]
                    elif stack[-2][1] == "unary":
                        t = ( (stack[-2][0], stack[-1]), "unary_exp")
                        stack[-2:]=[t]
                    elif stack[-2][1] == ':' and len(stack)>5 and stack[-4][1]=='?':
                        t = ( (stack[-5], stack[-3], stack[-1]), "conditional_exp")
                        stack[-5:]=[t]
                    else:
                        t = ( (stack[-2][1], stack[-3], stack[-1]), "binary_exp")
                        stack[-3:]=[t]
                    continue
            break
        if cur is None:
            continue
        if cur[1] == ';':
            stmt = stack.pop()
            got_statement(stmt)
            continue
        if cur[0] == "eof" and cur[1]==")":
            break
        elif cur[1]:
            stack.append(cur)
    return cur_context

def js_double_string(s):
    r_esc_extra = re.compile(r"\\([^0btnvfrxuX'\"\\])")
    s = r_esc_extra.sub(r'\1', s)
    return eval('"'+s+'"')

def js_single_string(s):
    r_double = re.compile('(?!\\)"')
    s = r.sub('\\"', s)
    return eval('"'+s+'"')

def get_token_value(var):
    if var[1]=="identifier":
        if var[0] in variables:
            return variables[var[0]]
        else:
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
            raise Exception(op+" on non-variable!")
        if op=='++':
            t+=1
        else:
            t-=1
        variables[token[0]]=t
        return t
    else:
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
        raise Exception("unhandled operator ["+op+"]")

def token(t, level):
    if t[1] == "identifier":
        s = str(t[0])
    elif t[1] in prime_type:
        s = repr(t[0])
    elif t[1]=="binary_exp":
        s = token(t[0][1], level+1)+' '+t[0][0]+' '+token(t[0][2], level+1)
    elif t[1]=="unary_exp":
        if re.match(r'\w', t[0][0][-1]):
            s = t[0][0]+' '+token(t[0][1], level+1)
        else:
            s = t[0][0]+token(t[0][1], level+1)
    elif t[1]=="postfix_exp":
        s = token(t[0][1], level+1)+t[0][0]
    elif t[1]=="list_exp":
        s = token_array(t[0])
    elif t[1]=="object":
        s = '{'+token(t[0], level+1)+'}'
    elif t[1]=="array":
        s = '['+token_array(t[0])+']'
    elif t[1]=="conditional_exp":
        s = token(t[0][0], level+1)+' ? '+token(t[0][1], level+1)+' : '+token(t[0][2], level+1)
    elif t[1]=="fcall":
        s = token(t[0][0], level+1)+'('+token(t[0][1], level+1)+')'
    elif t[1]=="index":
        s = token(t[0][0], level+1)+'['+token(t[0][1], level+1)+']'
    elif t[1]=="function":
        if "name" in t[0]:
            s_name = t[0]["name"]
        else:
            s_name = "-"
        s = s_name+'('+token(t[0]['param'], level+1)+')'+'{'+str(len(t[0]["statements"]))+' stmts}'
    else:
        s = None
    if s is None:
        return str(t)
    elif level>10:
        return s
    else:
        return "("+t[1]+", "+s+ ")"

def token_array(t):
    tlist=[]
    n=len(t)
    if n>0:
        tlist.append(token(t[0], 1))
        tlist.append("... "+str(n-1)+" more items")
    s = ', '.join(tlist)
    return s

def print_stack(stack):
    print("stack: ", end="")
    indent="    "
    for t in stack:
        print(indent, token(t, 0))
        if t[1]=="boc":
            indent+="    "
    print("\n")

re1 = re.compile(r"else\b")
re2 = re.compile(r"if\b")
re3 = re.compile(r"while\b")
re4 = re.compile(r"\s+")
re5 = re.compile(r"[ \t]+")
re6 = re.compile(r"//.*$", re.M)
re7 = re.compile(r"/\*.*?\*/", re.S)
re8 = re.compile(r"[\r\n]+")
re9 = re.compile(r"do\b")
re10 = re.compile(r"for\b")
re11 = re.compile(r"with\b")
re12 = re.compile(r"switch\b")
re13 = re.compile(r"try\b")
re14 = re.compile(r"var\b")
re15 = re.compile(r"(return|throw|break|continue)\b")
re16 = re.compile(r"default\b")
re17 = re.compile(r"case\b")
re18 = re.compile(r"([a-zA-Z_\$]\w*):")
re19 = re.compile(r"true|false")
re20 = re.compile(r"null\b")
re21 = re.compile(r"\"(([^\\\"]|\\.)*)\"")
re22 = re.compile(r"'(([^\\']|\\.)*)'")
re23 = re.compile(r"/([^\\/]|\\.)+/[igm]*")
re24 = re.compile(r"0x[0-9a-f]+", re.I)
re25 = re.compile(r"0[0-7]*", re.I)
re26 = re.compile(r"(\d+)(\.\d+)?([eE][+-]?\d+)?")
re27 = re.compile(r"[\[\(\{]")
re28 = re.compile(r"[\]\)\}]")
re29 = re.compile(r"\+\+|--")
re30 = re.compile(r"\.[a-zA-Z_\$]\w*")
re31 = re.compile(r"(new|in|delete|typeof|void|instanceof)\b")
re32 = re.compile(r"(==?=?|!==?|>>?>?=?|<<?=?|&&?|\|\|?)")
re33 = re.compile(r"[+\-*/%^&|]=?")
re34 = re.compile(r"[,~!\?]")
re35 = re.compile(r"function\b")
re36 = re.compile(r"[a-zA-Z_\$]\w*")
re37 = re.compile(r"[;\r\n]+")
re38 = re.compile(r"catch\b")
re39 = re.compile(r"finally\b")
if __name__ == "__main__":
    main()
