library(geodata)
library(terra)
library(dismo)
library(rJava)

setwd("/root/R")

# get raster from bioclim variable
lz_clim <- stack("lz_clim_data.tiff")
# Get presence data
presence <- read.csv("species_location.csv")

# get test sample data
presence <- presence[, c("longitude", "latitude")]
n_test <- sample(seq_len(nrow(presence)), nrow(presence) / 5)
test_data <- presence[n_test, ]
# remove the test sample from main data
train_data <- presence[-n_test, ] # notice the '-' operator

# make presence spatial
coordinates(presence) <- ~longitude + latitude

# Create the model
nicotiana.maxent <- dismo::maxent(
    stack(lz_clim), # predictors
    train_data
)

png(file = "variable_contribution.png")
plot(nicotiana.maxent)
dev.off()
# response(nicotiana.maxent) # idk what is this for yet


# Make the prediction based on the model
nicotiana.predict <- predict(
    object = nicotiana.maxent,
    x = lz_clim,
)
png(file = "prediction.png")
plot(nicotiana.predict)
plot(presence, add = TRUE)
dev.off()

# Export the prediction
writeRaster(nicotiana.predict, "nicotiana_predict.tiff", overwrite = TRUE)

# Evaluate
background <- randomPoints(stack(lz_clim), 200)
ev <- evaluate(
    model = nicotiana.maxent,
    p = test_data,
    a = background,
    x = stack(lz_clim)
)
png(file = "ROC.png")
plot(ev, "ROC")
dev.off()

