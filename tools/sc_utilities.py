def replace_param(filename, param, newparamstr, occurrence=1):
    """replace a namelist parameter in a Fortran namelist file"""

    comt = '!' # the comment character
    istatus = -1
    ierr = 0
    occ_counter = 0
    possible = False



    # check that newparamstr is of the form  param2 = val2    
    if not '=' in newparamstr:
        raise SkipError('replace_param: newparamstr should'
                        'be a string of the form "param2 = val2" ')
 
    # open file if exists
    try:
        data = open(filename).readlines()
    except:
        raise SkipError('replace_param: Error while opening '+filename)

    new_data = []
    
    for line in data:

        # remove end of line charcater
        line = line.strip('\n')
        # separates comments from rest of the line
        i_cmt = line.find(comt)
        if i_cmt == -1: i_cmt = len(line) # if no comments on this line
        line_c = line[i_cmt:]
        line = line[:i_cmt]
        
        # search for attention-relevant patterns, i.e. assignements
        matchobj = re.finditer(namelist_pattern,line)
        if matchobj is None:
            continue
        for assignement in matchobj:
            if assignement.group('varname') == param:
                # change the entige group with the newparamstring
                occ_counter += 1
                
                if occ_counter == occurrence:
                    line = line.replace(assignement.group(),newparamstr+',')
                    modification = True
                    possible = True
        
        new_data.append(line+line_c+'\n')
                             
    fout = open(filename,'w')
    fout.write(string.join(new_data,''))
    fout.close

    # if no return has been so far executed the code will have no significance any more
    if not possible:
        raise SkipError('replace_param: unable to succesfully find  paramenter '+param+' into '+newparamstr)

    if not modification:
        raise SkipError('replace_param: unable to succesfully modify the '+occurrence+
                        'th occurrence of paramenter '+param+' into '+newparamstr)

#get line matching pattern
#return empty string if no match
#--------------------------------------------
def get_line(filename,pattern):
    import re
    prog = re.compile(pattern)
    res=[]
    try:
        lines=open(filename).read().splitlines()
        for line in lines:
            if re.search(pattern,line):
                res.append(line)
    except:
        print '!! Error: get_line: cannot open %s' %filename

    return res
        
