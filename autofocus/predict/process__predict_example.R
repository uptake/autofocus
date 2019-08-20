#Examples of how to make requests agains the image classification endpoints
#Note: 
#   1. This assumes that the image_classifier_api is running 
#        (i.e., using docker run -p 8000:8000 gaganden/autofocus_serve)
#   2. It also assumes that the api address is at 127.0.0.1 
#        (which should be the case)
#   3. Assumes that your current working directory is 
#       './GitHub/autofocus/autofocus/predict'
#   4. Assumes that the images you are going to send to autofocus have
#        not been preprocessed at all. 

#Library requirements:
# RCurl, jsonlite, dplyr, magick, zip, progress

library(RCurl)
library(jsonlite)
library(magick)
library(zip)
library(progress)
library(dplyr)

find_image_files <- function(search_dir, 
                             image_list = c("jpeg","jpg","bmp","png", "JPG")){
  # Utility function to find all recursively find all image files 
  #   starting from a directory
  
  # Args:
  #   search_dir(character): the starting directory path from which to search
  #     image_list(list): a list of acceptable file formats
  
  # Returns:
  #   image_files(list): list containing the paths of all image files found. 
  #     Each element in this list is a vector of at least 10 images. This split
  #     is done so that the images can be zipped and sent to autofocus.
  
  file_list <- list.files(search_dir, recursive = TRUE, full.names = TRUE)
  image_files <- file_list[grep(paste(image_list, collapse = "|"), file_list)]
  image_files <- normalizePath(image_files, winslash = "/")
  # normalize the path, then split into groups of max 10 image
  n_groups <- ceiling(length(image_files) / 10)
  image_files <- split(image_files,
                       sort(rep_len(1:n_groups, length(image_files))))
  
  return(image_files)
}


process_images <- function(image_files = NULL){
  # Utility function to preprocess images to be sent to autofocus
  
  # Args:
  #   image_files(list): the output object from find_images()
  
  # Returns:
  #   a list: This list has two elements:
  #     1. zip(character): A vector of the temporary zip files to be sent to 
  #          autofocus.
  #     2. dict(named character): a key-value pair that links the temporary
  #          image file to the actual file. The elements in this vector are
  #          the names of the temporary files while the names are the full 
  #          paths to the file names.
  
  if(!is(image_files, 'list'))
    stop('image_files must be a list.')
  
  if(any(sapply(image_files, length)>10))
    stop('One of the elements is image_files has > 10 images.')
  
  dict_list <- vector('list', length = length(image_files))
  zip_vector <- rep(NA, length(image_files))
  
  cat(paste('Processing', length(unlist(image_files)), 'images...\n'))
  
  pb <- progress_bar$new(
    format = "Images processed [:bar] :elapsed | eta: :eta",
    total = length(unlist(image_files)),
    width = 60
  )

  for(photo_group in seq.int(length(image_files))){
    
    file_pattern <- paste0("file_",stringr::str_pad(1:length(image_files[[photo_group]]),
                               width = 2, pad = "0"),"_")
    # make some temporary file names
    tmp_name <- tempfile(pattern = file_pattern,
      fileext = rep('.jpg', 
      length(image_files[[photo_group]])))
    # sort them
    tmp_name <- sort(tmp_name)
    
    # dictionary to line up temps to actual photo
    dict <- sapply(strsplit(tmp_name, "\\\\|/"), function(x) x[length(x)])
    names(dict) <- image_files[[photo_group]]
    
    # Read in iamge, crop 198 from the bottom, resize to 512 pixels tall,
    #  then save as a temporary image.
    for(image in seq.int(length(image_files[[photo_group]]))){
      pb$tick()
      image_read(image_files[[photo_group]][image]) %>% 
      image_crop(., paste0(image_info(.)$width,
                               "x",
                               image_info(.)$height-198)) %>% 
        image_resize(., '760x512!') %>% 
        image_write(., tmp_name[image])
    }
    
    # zip the temporary files together
    tmp_zip <- tempfile(fileext = ".zip")
    zipr(tmp_zip, tmp_name)
    dict_list[[photo_group]] <- dict
    zip_vector[photo_group] <- tmp_zip
    if(file.exists(tmp_zip)){
      unlink(tmp_name)
    }
  }
    
    # return the dictionary and the name of the zipped file.
    return(list(zip = zip_vector, dict = dict_list))
  }





post_zips <- function(processed_images = NULL,
                      uri = "http://localhost:8000/predict_zip"){
  # send the zip files to autofocus
  
  # Args:
  #   processed_images(list): the output from process_images()
  #   uri(character): the location autofocus is running
  
  #Returns:
  #   response(tibble): A tibble of guesses for each image supplied to 
  #     autofocus. The columns, save for the last one, have species names
  #     and represent the likelihood that this species is in the image.
  #     The last column is the file name of the image.
cat(paste('Posting', length(processed_images$zip), 
          'zip file(s) to autofocus...\n'))

pb <- progress_bar$new(
  format = "Files processed [:bar] :elapsed | eta: :eta",
  total = length(unlist(processed_images$zip)),
  width = 60
)
# the object that initially contains the autofocus json
response <- vector('list', length(processed_images$zip))
for(zippy in seq.int(length(processed_images$zip))){
  pb$tick()
  # post to autofocus
  response[[zippy]] <- fromJSON(postForm(uri, 
                                        file = fileUpload(processed_images$zip[zippy]),
                                         .checkParams = FALSE))
  
  # get the file names from autofocus
  file_names <- strsplit(names(response[[zippy]]), "/")
  file_names <- sapply(file_names, function(x) x[length(x)])
  file_names <- strsplit(file_names, "_")
  file_names <- as.numeric(sapply(file_names, '[[', 2))
  # and line it up with what we did during image processing
  OG_file_names <- names(processed_images$dict[[zippy]])[file_names]
  # provide a warning just incase autofocus did not ID a specific image
  if(!length(OG_file_names) == length(processed_images$dict[[zippy]]) ){
    warning(paste('Autofocus did not ID all images in zip file number', zippy))
  }
  # put the file name into each nested list object
  for(image in seq.int(length(response[[zippy]]))){
    response[[zippy]][[image]]$file <- OG_file_names[image]
  }
}
# bind the list of lists, then bind the list of tibbles
response <- lapply(response, bind_rows) %>% bind_rows
return(response)
}

most_likely <- function(response_frame = NULL){
  # Utility function that provides the best guess from each classification
  
  # Args:
  #   response_frame(tibble): the output from post_zips()
  
  # Returns:
  #   A tibble that has three columns: 
  #     1) file: the file name
  #     2) species: the species most likely to be in the image
  #     3) probability autofocus's confidence of this classification
  
  # Find which column has the highest likelihood
  best_guess <- apply(response_frame[,-grep('file', colnames(response_frame))], 
                      1, which.max)
  # Grab the highest likelihood
  best_prob <- apply(response_frame[,-grep('file', colnames(response_frame))], 
                     1, max)
  # Correspond the highest likelihood to a species name
  species_name <- colnames(response_frame)[best_guess]
  
  # the object to return
  to_return <- tibble(file = response_frame$file,
                      species = species_name,
                      probability = best_prob)
  return(to_return)
}




# where are the photos located
search_dir <- "./images/"

all_images <- find_image_files(search_dir)

processed_images <- process_images(all_images)

my_ids <- post_zips(processed_images)

best_ids <- most_likely(my_ids)

