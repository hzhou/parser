import re

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
        else:
            t_context = stack[-1][0]
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
                            cur_context = last_context
                            stack.append(("if_cond", "boc"))
                            context_stack.append(cur_context)
                        else:
                            print("stack: ", stack);
                            raise Exception("if missing (")
                    else:
                        cur_context = last_context
                        stack.append(("if_block", "boc"))
                        context_stack.append(cur_context)
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
                        cur_context = last_context
                        stack.append(("do_cond", "boc"))
                        context_stack.append(cur_context)
                    else:
                        print("stack: ", stack);
                        raise Exception("while missing (")
                else:
                    print("stack: ", stack);
                    raise Exception("do missing while")
            elif t_context == "for_block":
                stmt = ( (cur_context["condition"], stmt), "for")
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
                stmt = (stmt, "return")
                got_statement(stmt)
            elif t_context=="case":
                stmt = (stmt, "case")
                got_statement(stmt)

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


    precedence = {'bof':0,'eof':0,'boc':0,'(':0,')':0,';':1,',':1,'=':2,'+=':2,'-=':2,'*=':2,'/=':2,'%=':2,'&=':2,'^=':2,'|=':2,'<<=':2,'>>=':2,'>>>=':2,'?':3,':':3,'||':4,'&&':5,'|':6,'^':7,'&':8,'==':9,'!=':9,'===':9,'!==':9,'instanceof':10,'in':10,'<':10,'<=':10,'>':10,'>=':10,'<<':11,'>>':11,'>>>':11,'+':12,'-':12,'*':13,'/':13,'%':13,'.':15,'unary':99}
    boc_type=['(', 'boc', 'bof', 'eof']
    atom_type=['']
    unary_type=[]
    right_precedences=[]
    context_stack = []
    cur_context = {'type':"global", 'statements':[]}
    last_context= None
    literal_type = ["bool", "null", "int", "float", "string"]
    number_type = ["int", "float", "num"]
    float_type  = ["float"]
    expr_type   = ["identifier"]
    expr_type.extend(["binary_exp", "unary_exp", "list_exp", "postfix_exp", "conditional_exp"])
    expr_type.extend(["member", "fcall", "index"])
    atom_type.extend(literal_type)
    atom_type.extend(number_type)
    atom_type.extend(expr_type)
    atom_type.append("object_item")
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
            # r"[a-zA-Z_\$]\w*"
            m = re9.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur = (m.group(0), "identifier")
                skip_space(0)
                if src_pos<src_len and src[src_pos]==':':
                    src_pos+=1
                    stmt = (cur[0], "label")
                    got_statement(stmt)
                    continue
                break
            # r"true|false"
            m = re10.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur = (m.group(0), "bool")
                break
            # r"null\b"
            m = re11.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur = (m.group(0), "null")
                break
            # r"\"(([^\\\"]|\\.)*)\""
            m = re12.match(src, src_pos)
            if m:
                src_pos=m.end()
                s=js_double_string(m.group(1))
                cur = (s, "string")
                break
            # r"'(([^\\']|\\.)*)'"
            m = re13.match(src, src_pos)
            if m:
                src_pos=m.end()
                s=js_single_string(m.group(1))
                cur = (s, "string")
                break
            # r"/([^\\]|\\.)+/[igm]*"
            m = re14.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur = (m.group(0), "regex")
                break
            # r"0x[0-9a-f]+", re.I
            m = re15.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur = (int(m.group(0), 16), "int")
                break
            # r"0[0-7]*", re.I
            m = re16.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur = (int(m.group(0), 8), "int")
                break
            # r"(\d+)(\.\d+)?([eE][+-]?\d+)?"
            m = re17.match(src, src_pos)
            if m:
                src_pos=m.end()
                if m.group(2) or m.group(3):
                    cur = (float(m.group(0)), "float")
                else:
                    cur = (int(m.group(1)), "int")
                break
            # r"[\[\(\{]"
            m = re18.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                if stack[-1][1] in atom_type:
                    if op == '(':
                        cur_context = {type:"fcall"}
                        stack.append(("fcall", "boc"))
                        context_stack.append(cur_context)
                    elif op== '[':
                        cur_context = {type:"index"}
                        stack.append(("index", "boc"))
                        context_stack.append(cur_context)
                    else:
                        print("stack: ", stack);
                        raise Exception("error opening bracket '"+op+"', forgot ';'?")
                else:
                    if op == '{':
                        if stack[-1][1]=='boc':
                            cur_context = {type:"compound"}
                            stack.append(("compound", "boc"))
                            context_stack.append(cur_context)
                            cur_context["statements"]=[]
                        else:
                            cur_context = {type:"object"}
                            stack.append(("object", "boc"))
                            context_stack.append(cur_context)
                    elif op == '[':
                        cur_context = {type:"array"}
                        stack.append(("array", "boc"))
                        context_stack.append(cur_context)
                    else:
                        stack.append(('(', '('))
                continue
            # r"[\]\)\}]"
            m = re19.match(src, src_pos)
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
            m = re20.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                if stack[-1][1] in atom_type:
                    stack[-1] = ( (op, stack[-1]), "postfix_exp")
                else:
                    stack.append((op, "unary"))
                continue
            # r"new|in|delete|typeof|void|instanceof"
            m = re21.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"(==?=?|!==?|>>?>?=?|<<?=?|&&?|\|\|?)"
            m = re22.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"[+\-*/%^&|]=?"
            m = re23.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"[,~!\?]"
            m = re24.match(src, src_pos)
            if m:
                src_pos=m.end()
                op = m.group(0)
                cur = (op, op)
                break
            # r"if\b"
            m = re2.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='(':
                    src_pos+=1
                    cur_context = {type:"if_cond"}
                    stack.append(("if_cond", "boc"))
                    context_stack.append(cur_context)
                    cur_context["branch_list"]=[]
                else:
                    print("stack: ", stack);
                    raise Exception("if missing (")
                continue
            # r"while\b"
            m = re3.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='(':
                    src_pos+=1
                    cur_context = {type:"while_cond"}
                    stack.append(("while_cond", "boc"))
                    context_stack.append(cur_context)
                    continue
                else:
                    print("stack: ", stack);
                    raise Exception("while missing (")
            # r"do\b"
            m = re25.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur_context = {type:"do_block"}
                stack.append(("do_block", "boc"))
                context_stack.append(cur_context)
                continue
            # r"for\b"
            m = re26.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='(':
                    src_pos+=1
                    cur_context = {type:"for_cond"}
                    stack.append(("for_cond", "boc"))
                    context_stack.append(cur_context)
                    cur_context["statements"]=[]
                    continue
                else:
                    print("stack: ", stack);
                    raise Exception("for missing (")
            # r"with\b"
            m = re27.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='(':
                    src_pos+=1
                    cur_context = {type:"with_cond"}
                    stack.append(("with_cond", "boc"))
                    context_stack.append(cur_context)
                    continue
                else:
                    print("stack: ", stack);
                    raise Exception("with missing (")
            # r"switch\b"
            m = re28.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='(':
                    src_pos+=1
                    cur_context = {type:"switch_cond"}
                    stack.append(("switch_cond", "boc"))
                    context_stack.append(cur_context)
                    continue
                else:
                    print("stack: ", stack);
                    raise Exception("switch missing (")
            # r"try\b"
            m = re29.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='{':
                    src_pos+=1
                    cur_context = {type:"try_block"}
                    stack.append(("try_block", "boc"))
                    context_stack.append(cur_context)
                    cur_context["statements"]=[]
                else:
                    print("stack: ", stack);
                    raise Exception("try missing {")
                continue
            # r"var\b"
            m = re30.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur_context = {type:"var"}
                stack.append(("var", "boc"))
                context_stack.append(cur_context)
                continue
            # r"var\b"
            m = re30.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur_context = {type:"return"}
                stack.append(("return", "boc"))
                context_stack.append(cur_context)
                continue
            # r"break|continue"
            m = re31.match(src, src_pos)
            if m:
                src_pos=m.end()
                type = m.group[0]
                skip_space(0)
                # r"[a-zA-Z_\$]\w*"
                m = re9.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    skip_space(0)
                    stmt = (m.group[0], type)
                else:
                    stmt = (None, type)
                # r"[;\r\n]+"
                m = re32.match(src, src_pos)
                if m:
                    src_pos=m.end()
                    got_statement(stmt)
                else:
                    print("stack: ", stack);
                    raise Exception("garbage after "+type)
                continue
            # r"default\b"
            m = re33.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]==':':
                    src_pos+=1
                    stmt = (None, "case")
                    got_statement(stmt)
                else:
                    print("stack: ", stack);
                    raise Exception("default label missing :")
                continue
            # r"case\b"
            m = re34.match(src, src_pos)
            if m:
                src_pos=m.end()
                cur_context = {type:"case"}
                stack.append(("case", "boc"))
                context_stack.append(cur_context)
                continue
            # r"function\b"
            m = re35.match(src, src_pos)
            if m:
                src_pos=m.end()
                skip_space(1)
                if src_pos<src_len and src[src_pos]=='(':
                    src_pos+=1
                    cur_context = {type:"function_param"}
                    stack.append(("function_param", "boc"))
                    context_stack.append(cur_context)
                    continue
                else:
                    print("stack: ", stack);
                    raise Exception("function missing (")
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
                            if t_atom[1]=="":
                                t_atom=[]
                            cur = (t_atom, "object")
                        elif t_context =="compound":
                            last_context["statements"].append(t_atom)
                            stmt = (last_context["statements"], "compound")
                            got_statement(stmt)
                        elif t_context =="if_cond":
                            cur_context = last_context
                            stack.append(("if_block", "boc"))
                            context_stack.append(cur_context)
                            cur_context["condition"]=t_atom
                        elif t_context == "while_cond":
                            cur_context = last_context
                            stack.append(("while_block", "boc"))
                            context_stack.append(cur_context)
                            cur_context["condition"]=t_atom
                        elif t_context == "do_cond":
                            stmt = ( (t_atom, last_context["block"]), "do_while")
                            stack.append(stmt)
                        elif t_context == "for_cond":
                            cur_context = last_context
                            stack.append(("for_block", "boc"))
                            context_stack.append(cur_context)
                            t_cond_list = cur_context["statements"]
                            t_cond_list.append(t_atom)
                            cur_context["condition"]=t_cond_list
                            del cur_context["statements"]
                        elif t_context == "with_cond":
                            cur_context = last_context
                            stack.append(("with_block", "boc"))
                            context_stack.append(cur_context)
                            cur_context["condition"]=t_atom
                        elif t_context == "switch_cond":
                            cur_context = last_context
                            stack.append(("switch_block", "boc"))
                            context_stack.append(cur_context)
                            cur_context["condition"]=t_atom
                        elif t_context =="try_block":
                            last_context["statements"].append(t_atom)
                            last_context["try_block"]=last_context["statements"]
                            del last_context["statements"]
                            last_context["catch_cond"]=None
                            last_context["catch_block"]=None
                            last_context["finally_block"]=None
                            # r"catch\b"
                            m = re36.match(src, src_pos)
                            if m:
                                src_pos=m.end()
                                skip_space(1)
                                if src_pos<src_len and src[src_pos]=='(':
                                    src_pos+=1
                                    cur_context = last_context
                                    stack.append(("catch_cond", "boc"))
                                    context_stack.append(cur_context)
                                else:
                                    print("stack: ", stack);
                                    raise Exception("catch missing (")
                            else:
                                stmt = ( last_context, "try")
                                got_statement(stmt)
                        elif t_context == "catch_cond":
                            last_context["catch_cond"] = t_atom
                            if src_pos<src_len and src[src_pos]=='{':
                                src_pos+=1
                                cur_context = last_context
                                stack.append(("catch_block", "boc"))
                                context_stack.append(cur_context)
                                cur_context["statements"]=[]
                            else:
                                print("stack: ", stack);
                                raise Exception("catch missing {")
                        elif t_context == "catch_block":
                            last_context["statements"].append(t_atom)
                            last_context["catch_block"]=last_context["statements"]
                            del last_context["statements"]
                            # r"finally\b"
                            m = re37.match(src, src_pos)
                            if m:
                                src_pos=m.end()
                                skip_space(1)
                                if src_pos<src_len and src[src_pos]=='{':
                                    src_pos+=1
                                    cur_context = last_context
                                    stack.append(("finally_block", "boc"))
                                    context_stack.append(cur_context)
                                    cur_context["statements"]=[]
                                else:
                                    print("stack: ", stack);
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
                                cur_context = last_context
                                stack.append(("function_block", "boc"))
                                context_stack.append(cur_context)
                                cur_context["statements"]=[]
                            else:
                                print("stack: ", stack);
                                raise Exception("function missing {")
                        elif t_context == "function_block":
                            last_context["statements"].append(t_atom)
                            cur = (last_context, "function")
                        break
                    elif stack[-2][1] == '(':
                        cur = stack[-1]
                        stack[-2:]=[]
                        break
                    elif stack[-2][1]==':' and cur_context["type"]=="object":
                        if stack[-4][1]==',' or stack[-4][1]=="boc":
                            t_name = stack[-3][0]
                            t = ( (t_name, stack[-1]), "object_item")
                        else:
                            print("stack: ", stack);
                            raise Exception("object colon in the wrong place")
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
        if cur[1] == "eof":
            break
        elif cur[1]:
            stack.append(cur)
    return cur_context

def js_double_string(s):
    r_esc_extra = re.compile(r"\\([^0btnvfrxuX'\"\\])")
    s = r_esc_extra.sub(r'\1', s)
    s = eval('"'+s+'"')

def js_single_string(s):
    r_double = re.compile('(?!\\)"')
    s = r.sub('\\"', s)
    s = eval('"'+s+'"')

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

re1 = re.compile(r"else\b")
re2 = re.compile(r"if\b")
re3 = re.compile(r"while\b")
re4 = re.compile(r"\s+")
re5 = re.compile(r"[ \t]+")
re6 = re.compile(r"//.*$", re.M)
re7 = re.compile(r"/\*.*?\*/", re.S)
re8 = re.compile(r"[\r\n]+")
re9 = re.compile(r"[a-zA-Z_\$]\w*")
re10 = re.compile(r"true|false")
re11 = re.compile(r"null\b")
re12 = re.compile(r"\"(([^\\\"]|\\.)*)\"")
re13 = re.compile(r"'(([^\\']|\\.)*)'")
re14 = re.compile(r"/([^\\]|\\.)+/[igm]*")
re15 = re.compile(r"0x[0-9a-f]+", re.I)
re16 = re.compile(r"0[0-7]*", re.I)
re17 = re.compile(r"(\d+)(\.\d+)?([eE][+-]?\d+)?")
re18 = re.compile(r"[\[\(\{]")
re19 = re.compile(r"[\]\)\}]")
re20 = re.compile(r"\+\+|--")
re21 = re.compile(r"new|in|delete|typeof|void|instanceof")
re22 = re.compile(r"(==?=?|!==?|>>?>?=?|<<?=?|&&?|\|\|?)")
re23 = re.compile(r"[+\-*/%^&|]=?")
re24 = re.compile(r"[,~!\?]")
re25 = re.compile(r"do\b")
re26 = re.compile(r"for\b")
re27 = re.compile(r"with\b")
re28 = re.compile(r"switch\b")
re29 = re.compile(r"try\b")
re30 = re.compile(r"var\b")
re31 = re.compile(r"break|continue")
re32 = re.compile(r"[;\r\n]+")
re33 = re.compile(r"default\b")
re34 = re.compile(r"case\b")
re35 = re.compile(r"function\b")
re36 = re.compile(r"catch\b")
re37 = re.compile(r"finally\b")
if __name__ == "__main__":
    main()
