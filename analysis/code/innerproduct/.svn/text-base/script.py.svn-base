'''the functions for the script. To run the script, run the function
interpret_and_run(args), with the value returned by parse_argument as args. The
script will take in command-line arguments and run pointwise product analysis
on data.'''

import os
import shutil
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pointwiseproduct import PointwiseProduct
from similaritydrawer import SimilarityDrawer
from code.common import exceptions
from code.common import filehandler


def parse_arguments():
    '''Parses the command-line arguments with argparse. Use -h for help.
    @return: the parsed arguments in a Namespace.
    @rtype: Namespace '''
    base_parser=get_base_parser()
    npz_base_parser=get_npz_base_parser()
    pic_base_parser=get_pic_base_parser()
    parser=argparse.ArgumentParser(
        description = 'Calculate and plot normalized pointwise product.' 
        + 'Use @filepath to read in arguments from a file', 
        fromfile_prefix_chars='@', 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers=parser.add_subparsers(
        title='subcommands', description='valid subcommands', 
        help='here are valid subcommands', dest='subcommand')
    run_parser=subparsers.add_parser(
        'run', parents=[base_parser, npz_base_parser, pic_base_parser], 
        help='Calculate the pointwise products and save them to a npz file,' 
        + 'and then use that file to save the graphical display of the' 
        + 'pointwise product. The saved files will be in a directory' 
        + 'placed in the same directory as the mce_file by default.',
        epilog='*All elements ignored will not be included in any analysis' 
        + ' and will not be plotted.', 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    npz_parser=subparsers.add_parser(
        'npz', parents=[base_parser, npz_base_parser], 
        help = 'Calculate the pointwise product and save them to a npz file. '
        + 'The saved file will be in a directory placed in ' 
        + 'the same directory as the mce_file by default.', 
        epilog='*All elements ignored will not be included in any analysis,', 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    pic_parser=subparsers.add_parser(
        'pic', parents=[base_parser, pic_base_parser], 
        help = 'Draws upon an npz file and plots the pointwiseproducts. ' 
        + 'The saved file will be in a directory placed in ' 
        + 'the same directory as the npz file by default.', 
        epilog='*All elements ignored will not be included in any plot '
        + 'analysis and will not be plotted.', 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    pic_parser.add_argument('npz_file',  nargs='?', 
        help='the file where the picture data will be read from.' 
        + 'This file is must be an npz file with the specific arrays.')
    return parser.parse_args()


def interpret_and_run(args):
    '''Interprets the arguments args, and does pointwise product analysis
    according to args.
    @param args: the arguments returned by parse_args(). These arguments will
    determine how the program is ran.
    @type args: Namespace '''
    for i in range (0, len(args.non_detectors)):
            args.non_detectors[i] = eval(args.non_detectors[i])
    if args.subcommand=='run' or args.subcommand=='npz':
        if args.mce_file==None:
            raise exceptions.StupidityError('No mce_file is specified.')
        if args.array_sum_filter==True:
            sum_filter='array_sum'
        elif args.column_filter==True:
            sum_filter='col_sum'
        elif args.row_filter==True:
            sum_filter='row_sum'
        else:
            sum_filter=None
        save_directory_path=initialize_data_save_directory(
            args.save_directory_name, args.mce_file,
            args.new_save_directory, sum_filter, 
            args.directory_save_location)    
        npz_file_path=run_pointwiseproduct(
            mce_file=args.mce_file, save_directory_path=save_directory_path, 
            sum_filter=sum_filter, non_columns=args.non_columns,
            non_rows=args.non_rows, non_detectors=args.non_detectors, 
            flipper=args.flipper)
    if args.subcommand=='run' or args.subcommand=='pic':
        if args.subcommand=='pic':
            if args.npz_file ==None:
                raise exceptions.StupidityError('No npz_file is specified.')
            else:
                npz_file_path=args.npz_file
            picture_directory_path=initialize_picture_directory(
                npz_file_path=npz_file_path, 
                picture_directory_name=args.picture_directory_name, 
                new_picture_directory=args.new_save_directory)
        elif args.subcommand=='run':
            picture_directory_path=initialize_picture_directory(
                npz_file_path=npz_file_path, 
                picture_directory_name=args.picture_directory_name, 
                new_picture_directory=True)
        if args.limit_range==None and args.limit_keyword==None:
            limit='non_auto'
        elif args.limit_range!=None and args.limit_keyword==None:
            limit=eval(args.limit_range)
        elif args.limit_keyword!=None and args.limit_range==None:
            if args.limit_keyword=='all':
                limit=(-1,1)
            else:
                limit=args.limit_keyword
        else:
            raise exceptions.IdenticalStateElectronBug(
                'Both limit_keyword and limit_range have been passed through' 
                + ' argparse, despite them being mutually exclusive.')
        run_similaritydrawer(
            npz_file_path=npz_file_path, 
            picture_directory_path=picture_directory_path, 
            non_columns=args.non_columns, non_rows=args.non_rows, 
            non_detectors=args.non_detectors, cut_nons=args.cut_nons, 
            limit=limit, 
            column_vs_column=args.column_vs_column, row_vs_row=args.row_vs_row)


def get_base_parser():
    '''Script internal function. Gets the base parser.  
    @return: the base parser. The base parser has all the arguments that is
    common to all subcommands.
    @rtype: argparse.ArgumentParser.'''
    base_parser=argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        '-nsd', '--new_save_directory', action='store_true', default=False, 
        help='If an old directory with the same name as the save directory ' 
        + 'exists, keep it and create a new directory to keep the new data.', 
        dest='new_save_directory')
    base_parser.add_argument('-nc', '--non_columns', nargs='*', default=[], 
                             type=int, help='the columns to be ignored.', 
                             dest='non_columns')
    base_parser.add_argument('-nr', '--non_rows', nargs='*', default=[], 
                             type=int, help='the rows to be ignored.', 
                             dest='non_rows')
    base_parser.add_argument('-nd', '--non_detectors', nargs='*', default=[], 
                             help='individual detectors to be ignored.' 
                             + ' Detectors are represented as (column, row)*.', 
                             dest='non_detectors')
    return base_parser


def get_npz_base_parser():
    '''Script internal function. Gets the npz-base parser.
    @return: the npz-base parser. The npz-base parser has all the arguments
    that is common to all both the run subcommand and the npz subcommand.
    @rtype: argparse.ArgumentParser.'''
    npz_base_parser=argparse.ArgumentParser(add_help=False)
    npz_base_parser.add_argument(
        'mce_file', nargs='?', 
        help='the file where the mce data will be read from.' 
        + 'This file is read with mce_data.SmallMCEFile. Read function.')
    npz_base_parser.add_argument(
        '-dsl', '--directory_save_location',
        help = 'The location to place the save directory. If None, ' 
        + 'the save directory will be placed in the same directory '
        + 'as the mce_file.' ,
        dest = 'directory_save_location')
    npz_base_parser.add_argument(
        '-sdn', default='stuff', 
        help = 'the tag of the directory where the analysis will be saved.'
        + ' This tag will be appended to a generated name to create'
        + ' the name of the save directory.', 
        dest='save_directory_name')
    npz_base_parser.add_argument(
        '-flp', '--flipper', 
        help = 'Indicates how the columns should be flipped. ' 
        + 'The column is the second dimension. The input is to be a tuple ' 
        + 'with length equal to the number of columns. '
        + '1 means not flipped, while -1 means flipped.',
        dest = 'flipper')
    sum_filter_group=npz_base_parser.add_mutually_exclusive_group()
    sum_filter_group.add_argument(
        '-af', action='store_true', default=False, 
        help='filters out the sum of all the timestreams.', 
        dest='array_sum_filter')
    sum_filter_group.add_argument(
        '-rf', action='store_true', default=False, 
        help='for each row of data, filters out the sum of that row.', 
        dest='row_filter')
    sum_filter_group.add_argument(
        '-cf', action='store_true', default=False, 
        help='for each column of data, filters out the sum of that column.', 
        dest='column_filter')
    return npz_base_parser


def get_pic_base_parser():
    '''Script internal function. Gets the pic-base parser.
    @return: the pic-base parser. The pic-base parser has all the arguments
    that is common to all both the run subcommand and the pic subcommand.
    @rtype: argparse.ArgumentParser.'''
    pic_base_parser=argparse.ArgumentParser(add_help=False)
    pic_base_parser.add_argument(
        '-pdn', default='drawings', 
        help = 'the tag of the directory where the pictures will be saved.'
        + 'This tag will be appended to a generated name to create'
        + ' the name of the save directory.', 
        dest='picture_directory_name')
    pic_base_parser.add_argument(
        '-cn', action='store_true', default=False, 
        help='cut out the non_rows and non_columns so they are not shown.' 
        + ' Normally, they are shown as white.', 
        dest='cut_nons')
    pic_base_parser.add_argument(
        '-cvc', '--column_vs_column', nargs='*', default=[],
        help = 'Plot the pointwise product of all rows in a column vs all '
        + 'rows in another column. The two columns are specified with (x, y).',
        dest = 'column_vs_column')
    pic_base_parser.add_argument(
        '-rvr', '--row_vs_row', nargs='*', default=[], 
        help = 'Plot the pointwise product of all columns in a row vs all ' 
        + 'columns in another row. The two rows are specified with (x, y).',
        dest = 'row_vs_row')
    limit_group=pic_base_parser.add_mutually_exclusive_group()
    limit_group.add_argument(
        '-lr', '--limit_range', default=None, 
        help = 'Limit the data. ' 
        + 'Plot everything outside of the limit as if they are at the limit.' 
        + ' If (x,y) is entered, the data will be limited to (x,y).', 
        dest='limit_range')
    limit_group.add_argument(
        '-lk', '--limit_keyword', default=None, 
        choices=['non_auto', 'full', 'all'], 
        help="Limit the data. " + 
        "Plot everything outside of the limit as if they are at the limit. " 
        + "non_auto: set the limit to min and max of data, ignoring diagonal;" 
        + " full:set the limit to min and max of data;" 
        + " all:set the limit to (-1,1)", 
        dest='limit_keyword')
    return pic_base_parser


def initialize_data_save_directory(save_directory_name, mce_file, 
                                   new_save_directory, sum_filter, 
                                   directory_save_location):
    '''Script internal function. Sets up data save directory for a mce_file,
    the overall save directory for the npz file, and possibly the drawing
    folders. This function is used in the run and npz subcommand. The name
    proper (without the directory path) of the file will be the name proper of
    the mce_file with sum_filter and save_directory_name appended.
    @return: the whole path of the data save directory.
    @rtype: str
    @param save_directory_name: a suffix to the data save directory
    @type save_directory_name: str
    @param mce_file: The whole path of the mce_file that the data save
    directory is for.
    @type mce_file: str 
    @param new_save_directory: indicates whether or not a new directory is to
    be created if there is already one with the same name. If False, the
    current directory will be deleted.
    @type new_save_directory: boolean
    @param sum_filter: indicates how the data was filtered by
    PointwiseProduct. This information is appended to the name of the
    directory.
    @type sum_filter: str
    @param directory_save_location: the directory in which the data save
    directory is to be saved in. If None, the data save directory will be saved
    in the same directory as the mce file.
    @type directory_save_location: str '''
    if os.path.exists(mce_file)==False:
        raise ValueError('The specified mce_file does not exist')
    if directory_save_location==None:
        save_directory_prefix=mce_file
    else:
        if os.path.exists(directory_save_location):
            save_directory_prefix = os.path.join(directory_save_location,
                                                 os.path.split(mce_file)[1])
        else:
            raise ValueError('The directory_save_location does not exist')
    if sum_filter!=None:
        save_directory_path=(save_directory_prefix + '_' + sum_filter 
                             + '_filtered_' + save_directory_name)
    else:
        save_directory_path=(save_directory_prefix + '_unfiltered_' 
                             + save_directory_name)
    if new_save_directory:
        original_save_directory_path=save_directory_path
        copy_number=1
        while os.path.exists(save_directory_path):
            copy_number+=1
            save_directory_path=(original_save_directory_path 
                                 + '_copy(' + str(copy_number) + ')')
    else:
        if os.path.exists(save_directory_path):
            shutil.rmtree(save_directory_path)
    os.mkdir(save_directory_path)
    return save_directory_path


def initialize_picture_directory(npz_file_path, picture_directory_name, 
                                 new_picture_directory):
    '''Script internal function. Sets up the directory for the pictures.
    @return: the whole path of the picture directory.
    @rtype: str    
    @param npz_file_path: the whole path of the npz file from which the
    pictures will be drawn. The picture directory will be placed in the save
    directory as the npz_file_path.
    @type npz_file_path: str
    @param picture_directory_name: The name proper (without the directory path)
    of the directory for the pictures.
    @type picture_directory_name: str
    @param new_picture_directory: indicates whether or not a new directory is
    to be created if there is already one with the same name. If False, the
    current directory will be deleted.
    @type new_picture_directory: boolean '''
    picture_directory_path=os.path.join(os.path.dirname(npz_file_path),
                                        picture_directory_name)
    if os.path.exists(npz_file_path)==False:
        raise ValueError('The specified mce_file does not exist')
    if os.path.exists(picture_directory_path)==True:
        if new_picture_directory:
            original_picture_directory_path=picture_directory_path
            copy_number=1
            while os.path.exists(picture_directory_path):
                copy_number+=1
                picture_directory_path=(original_picture_directory_path 
                                        + '_copy(' + str(copy_number) + ')')
        else:
            shutil.rmtree(picture_directory_path)
    os.mkdir(picture_directory_path)
    return picture_directory_path


def run_pointwiseproduct(mce_file, save_directory_path, sum_filter, 
        non_columns, non_rows, non_detectors, flipper):
    '''Script internal function. Generates an npz file with the to_file
    function of PointwiseProduct class according to the parameters. The npz
    file will have arrays dealing with the pointwise product of data in an mce
    file.
    @param mce_file: the whole mce file path from which the pointwise product
    will be calculated. This file will be read by the mce_data module.
    @type mce_file: str
    @param save_directory_path: the directory path where the npz file will be
    saved in.
    @type save_directory_path: str
    @param sum_filter: indicates the filter type of the data. This parameter is
    passed directly into PointwiseProduct. Options are None, 'array_sum',
    'col_sum', and 'row_sum'.
    @type sum_filter: str
    @param non_columns: the columns to set to zero. These columns will not
    affect any calculations.
    @type non_columns: tuple/list/numpy array, shape:(*)
    @param non_rows: the rows to set to zero. These rows will not affect any
    calculations.
    @type non_rows: tuple/list/numpy array, shape:(*)
    @param non_detectors: the detectors to set to zero. These detectors will
    not affect any calculations.
    @type non_detectors: list/numpy array, shape:(*,2) 
    @param flipper: indicates how to flip the columns in the data. If None, the
    data is not flipped. This parameter will be passed into eval(), and must
    result in a list or tuple of length equal to the number of columns. -1
    flips the column, while 1 does not.
    @type flipper: str '''
    mce_data=filehandler.get_mce_data(mce_file, row_col=True)
    if flipper!=None:
        flipper=eval(flipper)
        if len(flipper)==mce_data.shape[1]:
            for i in range(0, len(flipper)):
                mce_data[:,i,:]=flipper[i]*mce_data[:,i,:]
        else:
            raise ValueError (
                'The length of flipper different from the number of columns.')
    pointwise_product_analyzer=PointwiseProduct(
        mce_data, non_cols=non_columns, non_rows=non_rows, 
        non_elements=non_detectors, sum_filter=sum_filter)
    npz_file_path=os.path.join(save_directory_path, 'undescribed_file.npz')
    pointwise_product_analyzer.to_file(npz_file_path)
    return npz_file_path

    
def run_similaritydrawer(npz_file_path, picture_directory_path, 
                         non_columns, non_rows, non_detectors, cut_nons, 
                         limit, column_vs_column, row_vs_row):
    '''Script internal function. Draws pictures with an npz file using the
    module similaritydrawer.
    @param npz_file_path: the whole filepath from where data will be read. The
    data will be used to draw the pictures. The npz file should be one created
    by PointwiseProduct.to_file function.
    @type npz_file_path: str
    @param picture_directory_path: the whole path of the directory where the
    pictures are to be saved.
    @type picture_directory_path: str
    @param non_columns: the columns to be ignored. These columns will not be
    used in any analysis and will not be drawn.
    @type non_columns: tuple/list/numpy array, shape:(*)
    @param non_rows: the rows to be ignored. These rows will not affect any be
    used in any analysis and will not be drawn.
    @type non_rows: tuple/list/numpy array, shape:(*)
    @param non_detectors: the detectors to be ignored. These detectors will not
    be used in any analysis and will not be drawn..
    @type non_detectors: list/numpy array, shape:(*,2) 
    @param cut_nons: indicate whether or not the non_columns and non_rows will
    be cut in plots. If True, they will be cut out of the plot. If False, they
    will be shown as white. 
    @type cut_nons: boolean
    @param limit: the class_limit for similarity drawer. This parameter can be
    None, 'full', 'non_auto', 'inliers' or (x, y).
    @type limit: str; tuple, shape:(*)
    @param column_vs_column: a list of column vs column pointwise products to
    be plotted. Each column vs column is to be represented by a string '(x,y)',
    where x and y are the column numbers.
    @type column_vs_column: list of str
    @param row_vs_row: a list of row vs row pointwise products to be
    plotted. Each row vs row is to be represented by a string '(x,y)', where x
    and y are the row numbers.
    @type row_vs_row: list of str '''
    npz_dict=np.load(npz_file_path)
    similarity_drawer=SimilarityDrawer(
        npz_dict, non_cols=non_columns, non_rows=non_rows, 
        non_detectors=non_detectors, cut_nons=cut_nons, class_limit=limit)
    similarity_drawer.plot_data_data(dominance='column')
    plt.savefig(picture_directory_path 
                + '/Column_Dominated_Pointwise_Product_of_All_Data')
    similarity_drawer.plot_data_data(dominance='row')
    plt.savefig(picture_directory_path 
                + '/Row_Dominated_Pointwise_product_of_All_Data')
    for col in range(0, similarity_drawer.number_of_cols):
        try:
            similarity_drawer.plot_col_sum_col_data(col)
        except exceptions.ExistenceError:
            continue
        else:
            plt.savefig(
                picture_directory_path + 
                '/Pointwise_Product_between_All_Data_and_the_Sum_of_Col_'
                + str(col))
    for row in range(0, similarity_drawer.number_of_rows):
        try:
            similarity_drawer.plot_row_sum_row_data(row)
        except exceptions.ExistenceError:
            continue
        else:
            plt.savefig(
                picture_directory_path 
                + '/Pointwise_Product_between_All_Data_and_the_Sum_of_Row_' 
                + str(row))
    similarity_drawer.plot_array_sum_data()
    plt.savefig(picture_directory_path
                + '/Pointwise_Product_between_All_Data_and_the_Sum_of_Row_'
                + str(row))
    similarity_drawer.plot_col_sum_col_sum()
    plt.savefig(picture_directory_path
                + '/Pointwise_Product_between_Sum_of_Rows_in_Cols'
                + '_and_Sum_of_Rows_in_Cols')
    similarity_drawer.plot_row_sum_row_sum()
    plt.savefig(picture_directory_path
                + '/Pointwise_Product_between_Sum_of_Cols_in_Rows'
                + '_and_Sum_of_Cols_in_Rows')
    for col_col in column_vs_column:
        col_col=eval(col_col)
        try: 
            similarity_drawer.plot_single_block(col_col[0], col_col[1], 
                                                dominance='column')
        except exceptions.ExistenceError:
            print ('Failed to plot Col' + str(col_col[0]) + ' vs ' 
                   + str(col_col[1]) + ' because one of them is in non_cols')
        else:
            plt.savefig(picture_directory_path 
                        + '/Pointwise_Product_between_Col_' + str(col_col[0]) 
                        + '_and_Col_' +str(col_col[1]))
    for row_row in row_vs_row:
        row_row=eval(row_row)
        try: 
            similarity_drawer.plot_single_block(row_row[0], row_row[1], 
                                                dominance='row')
        except exceptions.ExistenceError:
            print ('Failed to plot Row' + str(row_row[0]) + ' vs ' 
                   + str(row_row[1]) + ' because one of them is in non_rows')
        else:
            plt.savefig(picture_directory_path 
                        + '/Pointwise_Product_between_Row_' + str(row_row[0]) 
                        + '_and_Row_' + str(row_row[1]))
