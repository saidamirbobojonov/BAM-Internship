#######################################################################################################################################################################

filenames = ['SXY_605MPa'] #Names of ansys_input's output files

#######################################################################################################################################################################

sign_delete = ['!cdwrite,db,_name1_,db'] #Delete sign '!' for rows in that rows which have '!' from 'Input_Ansys_Temp.inp' for  output file

#target_words is that word which programm will change for replacement_words in output file !!!!!!!!!! it comes defaultly so don't touch it, but if you need change you need ask from experts
target_words =['_Elem_Orient_', '_CE_1_', '_CE_2_', '_CE_3_', '_sxxp_', '_sxxm_', '_sxyp_', '_sxym_', '_sxzp_', '_sxzm_', '_syxp_', '_syxm_', '_syyp_', '_syym_', '_syzp_', '_syzm_', '_szxp_', '_szxm_', '_szyp_', '_szym_', '_szzp_', '_szzm_', '_name1_']
#######################################################################################################################################################################

replacement_words = {
    f'{filenames[0]}': [
        '_red_orient_972_G_R0',
        '!/input,../Ansys_Input_Files/CE_Def_X,dat',
        '!/input,../Ansys_Input_Files/CE_Def_Y,dat',
        '/input,../Ansys_Input_Files/CP_Def,dat',
        '300', '-300', '300', '-300','0', '0',
        '300', '-300', '300', '-300', '0', '0',
        '0', '0', '0', '0', '0', '0',
        f'{filenames[0]}'
    ]
}

#     for this template you need write your option for this variables in 'ansys_input' output file and what you gonna write that will be in 'ansys_input' output file'''

#     for this: f'{filenames[array_index]}' you just need change array_index to filenames's array, for example:
#     you have ----  filenames = ['SXY_605MPa','SXY_635MPa', 'SXY_655MPa']
#     if you want create ansys_input for 'SXY_605MPa' you need put f'{filenames[there should be index of 'sxy_605mpa']}'
#     so it gonna be f'{filenames[0]}' because for array index start from '0' and then for other ones
#     for each output file you need using Template

''' 
Template 
f'{filenames[array_index]}': [
        '_Elem_Orient_',
        '_CE_1_',
        '_CE_2_',
        '_CE_3_',
        '_sxxp_', '_sxxm_', '_sxyp_', '_sxym_', '_sxzp_', '_sxzm_',
        '_syxp_', '_syxm_', '_syyp_', '_syym_', '_syzp_', '_syzm_',
        '_szxp_', '_szxm_', '_szyp_', '_szym_', '_szzp_', '_szzm_',
        f'{filenames[array_index]}'
    ]
'''
#######################################################################################################################################################################
