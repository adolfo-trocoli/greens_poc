library(raster, quietly=TRUE)

args = commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
    stop("pass first longitude then latitude", call. = FALSE)
}
# change from string to numeric
args <- as.numeric(args)
setwd("/root/R/")
# actual_location <- c(-13.73650, 28.96590) # get from cli
actual_location <- args
# get the raster
r <- raster("nicotiana_predict.tiff")
# get the cell number where these coords lands in the raster
actual_cell <- cellFromXY(r, actual_location)
# get the cell number of the 8 adjacent to the actual cell, queen's case
around <- adjacent(r, actual_cell, direction = 8, pairs = FALSE)
# get the values of these cells
values_around <- r[around]
# determine which cell has the maximum value
next_cell <- around[which.max(values_around)]
next_location <- xyFromCell(r, next_cell)

invisible(sapply(next_location, cat, "\n"))

write(next_location, file = "next_location.txt", append = TRUE, sep = ", ")
