#Examples of how to make requests agains the image classification endpoints
#Note: 
#   1. This assumes that the image_classifier_api is running (i.e., using docker compose up)
#   2. It also assumes that the api address is at 127.0.0.1 (which should be the case)

#Library requirements:
# RCurl, jsonlite, data.table

library(RCurl)
library(jsonlite)


#####################
#SINGLE FILE EXAMPLE#
#####################

#The example below illustrates how to pass a set of files to the single file endpoint
#If you have a lot of images, this will  be a lot slower than zipping those images into a single file and 
#using the predict_zip endpoint

find_image_files <- function(search_dir, image_list = c("jpeg","jpg","bmp","png")){
  #Utility function to find all recursively find all image files starting from a directory

  # Args:
  #   search_dir(character): the starting directory path from which to search
  #   image_list(list): a list of acceptable file formats
  
  #Returns:
  #   image_files(list): list containing the paths of all image files found
  
  file_list = list.files(search_dir, recursive = T)
  image_list_collapse = paste(image_list, collapse = "|")
  image_files = file_list[grep(image_list_collapse, file_list)]
  return(paste0(search_dir, image_files))
}


search_dir = '/Users/dacheson/repos/image-classifier-api/'
image_files = find_image_files(search_dir)

#This is the endpoint
uri = 'http://127.0.0.1/predict'

#Loop through all image files and get the response
response_list = list()
for(img_path in image_files){
  response = tryCatch(
    {fromJSON(postForm(uri, file = fileUpload(img_path)))},
    error=function(cond) {
      message(paste("Something went wrong with the request becuase of:\n ",cond))
      return(NA)
    }
  )
  
  if(!(is.na(response))){
    response_list[[x]] =  fromJSON(postForm(uri, file = fileUpload(img_path)))
  }
}

#combine all predictions into a single data.table
predictions = data.table::rbindlist(response_list)



#################
#ZipFIle Example#
#################

#The example below illustrates how to pass a single zipfile to the predict_zip endpoint
#This will be much faster if you have a lot of images, although their may be some limitations on the size of the file
#you send in. 
#Note that the zipfile enpoint can handle directories and subdirectories, as well as files that aren't images

uri = 'http://127.0.0.1/predict_zip'
zipfile = '/Users/dacheson/repos/image-classifier-api/app/test.zip'

response = fromJSON(postForm(uri, file = fileUpload(zipfile)))

#response is returned as a list of objects, so just combine into a dataframe
predictions = data.frame(response)
