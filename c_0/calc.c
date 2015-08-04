#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

typedef int bool;
#define true 1
#define false 0

#define T_eof 1
#define T_num 2
#define T_Plus 3
#define T_Minus 4
#define T_Mult 5
#define T_Div 6
#define T_UMinus 7
#define T_MAX 8

struct token {
    int type;
    float val;
};

struct input_buffer {
    unsigned char * buffer;
    int n_pos;
    int n_end;
    int s[10];
    int e[10];
};

float calc(char * s);
bool match_eof(struct input_buffer * input);
bool match_re_1(struct input_buffer * input);
bool match_re_2(struct input_buffer * input);
bool match_re_3(struct input_buffer * input);
int input_get_char(struct input_buffer * input);
void * f_darray_expand(void * P, int n_rec_size, int* pn_size);
void input_back_char(struct input_buffer * input);

int op_table[T_MAX];

int main(int argc, char** argv){
    char * s;
    float f_ans;

    op_table[T_eof] = 0;
    op_table[T_num] = -1;
    op_table[T_Plus] = 1;
    op_table[T_Minus] = 1;
    op_table[T_Mult] = 2;
    op_table[T_Div] = 2;
    op_table[T_UMinus] = 99;
    s = strdup("1+2*-3");
    f_ans = calc(s);
    printf("ans = %g\n", f_ans);
    return 0;
}

float calc(char * s){
    struct input_buffer local_input_buffer;
    struct input_buffer * input;
    struct token * stack = NULL;
    int stack_len = 0;
    int stack_size = 0;
    struct token cur;
    char * ts_group;
    int tn_c;
    float tf_val;

    input = &local_input_buffer;
    input->buffer = s;
    input->n_pos = 0;
    input->n_end = strlen(s);
    while(1){
        while(1){
            if(match_eof(input)){
                cur.type = T_eof;
                cur.val = 0;
                break;
            }
            // /\s+/
            if(match_re_1(input)){
                continue;
            }
            // /[\d\.]+/
            if(match_re_2(input)){
                ts_group = input->buffer + input->s[0];
                tn_c = input->buffer[input->e[0]];
                input->buffer[input->e[0]] = 0;
                tf_val = atof(ts_group);
                input->buffer[input->e[0]] = tn_c;
                cur.type = T_num;
                cur.val = tf_val;
                break;
            }
            // /[-+*\/]/
            if(match_re_3(input)){
                ts_group = input->buffer + input->s[0];
                if(ts_group[0] == '+'){
                    cur.type = T_Plus;
                    cur.val = 0;
                }
                else if(ts_group[0] == '-'){
                    cur.type = T_Minus;
                    cur.val = 0;
                }
                else if(ts_group[0] == '*'){
                    cur.type = T_Mult;
                    cur.val = 0;
                }
                else if(ts_group[0] == '/'){
                    cur.type = T_Div;
                    cur.val = 0;
                }
                break;
            }
            tn_c = input_get_char(input);
        break;}
        while(1){
            if(cur.type == T_num){
                break;
            }
            if(stack_len < 1 || stack[stack_len-1].type != T_num){
                if(cur.type == T_Minus){
                    cur.type = T_UMinus;
                }
                else{
                    fprintf(stderr, "operator in wrong context");
                    exit(-1);
                }
                break;
            }
            if(stack_len < 2){
                break;
            }
            if(op_table[cur.type] <= op_table[stack[stack_len-2].type]){
                if(stack[stack_len-2].type == T_UMinus){
                    tf_val = -stack[stack_len-1].val;
                    stack_len -= 2;
                    if(stack_len + 1 > stack_size){
                        stack = f_darray_expand(stack, sizeof(struct token), &stack_size);
                    }
                    stack[stack_len].type = T_num;
                    stack[stack_len].val = tf_val;
                    stack_len++;
                }
                else{
                    if(stack[stack_len-2].type == T_Plus){
                        tf_val = stack[stack_len-3].val + stack[stack_len-1].val;
                    }
                    else if(stack[stack_len-2].type == T_Minus){
                        tf_val = stack[stack_len-3].val - stack[stack_len-1].val;
                    }
                    else if(stack[stack_len-2].type == T_Mult){
                        tf_val = stack[stack_len-3].val * stack[stack_len-1].val;
                    }
                    else if(stack[stack_len-2].type == T_Div){
                        tf_val = stack[stack_len-3].val / stack[stack_len-1].val;
                    }
                    stack_len -= 3;
                    if(stack_len + 1 > stack_size){
                        stack = f_darray_expand(stack, sizeof(struct token), &stack_size);
                    }
                    stack[stack_len].type = T_num;
                    stack[stack_len].val = tf_val;
                    stack_len++;
                }
                continue;
            }
        break;}
        if(cur.type != T_eof){
            if(stack_len + 1 > stack_size){
                stack = f_darray_expand(stack, sizeof(struct token), &stack_size);
            }
            stack[stack_len] = cur;
            stack_len++;
        }
        else{
            if(stack_len == 1){
                return stack[0].val;
            }
            else{
                fprintf(stderr, "error");
                exit(-1);
            }
        }
    }
    if(stack_size > 0){
        free(stack);
    }
}

bool match_eof(struct input_buffer * input){
    int tn_c;

    tn_c = input_get_char(input);
    if(tn_c <= 0 && input->n_pos >= input->n_end){
        return 1;
    }
    else{
        input_back_char(input);
        return 0;
    }
}

bool match_re_1(struct input_buffer * input){
    int tn_cnt_1 = 0;
    int tn_c;

    // /\s+/ 
    input->s[0] = input->n_pos;
    while(1){
        tn_c = input_get_char(input);
        if(isspace(tn_c)){
            tn_cnt_1++;
        }
        else{
            input_back_char(input);
            break;
        }
    }
    if(tn_cnt_1>0){input->e[0]=input->n_pos;return true;}else{return false;}
}

bool match_re_2(struct input_buffer * input){
    int tn_cnt_1 = 0;
    int tn_c;

    // /[\d\.]+/ 
    input->s[0] = input->n_pos;
    while(1){
        tn_c = input_get_char(input);
        if(isdigit(tn_c) || tn_c=='.'){
            tn_cnt_1++;
        }
        else{
            input_back_char(input);
            break;
        }
    }
    if(tn_cnt_1>0){input->e[0]=input->n_pos;return true;}else{return false;}
}

bool match_re_3(struct input_buffer * input){
    int tn_c;

    // /[-+*\/]/ 
    input->s[0] = input->n_pos;
    tn_c = input_get_char(input);
    if(tn_c=='-' || tn_c=='+' || tn_c=='*' || tn_c=='/'){
        input->e[0]=input->n_pos;return true;
    }
    else{
        input_back_char(input);
        return false;
    }
}

int input_get_char(struct input_buffer * input){
    int tn_c;

    if(input->n_pos < input->n_end){
        tn_c = input->buffer[input->n_pos];
        input->n_pos++;
        return tn_c;
    }
    else{
        input->n_pos++;
        return -1;
    }
}

void * f_darray_expand(void * P, int n_rec_size, int* pn_size){
    int tn_temp;

    tn_temp = (*pn_size) * 2 / 3;
    if(tn_temp < 64){
        tn_temp = 64;
    }
    (*pn_size) += tn_temp;
    P = realloc(P, (*pn_size) * n_rec_size);
    return P;
}

void input_back_char(struct input_buffer * input){
    if(input->n_pos > 0){
        input->n_pos--;
    }
}

