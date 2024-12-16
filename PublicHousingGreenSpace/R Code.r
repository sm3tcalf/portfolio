library(tidyverse)
setwd("C:/Users/samdm/OneDrive/Desktop/geog4060finalproj/outputs")
cityData <- tibble(read.csv("output.csv", header=FALSE))
colnames(cityData) <- c("City", "Code", "Mean")

onlyCWs <- filter(cityData, cityData$Code == "Citywide")
onlyPHs <- filter(cityData, cityData$Code != "Citywide")

meanPHs <- aggregate(x= onlyPHs$Mean,
                       by = list(onlyPHs$City),      
                       FUN = mean)
colnames(meanPHs) <- c("City", "PHMean")


joinTable <- merge(x = onlyCWs, y = meanPHs, by = "City", all = TRUE)
compareCWs_PHs <- subset(joinTable, select = -c(Code))
compareCWs_PHs <- compareCWs_PHs[-7,] #removes Columbus

colnames(compareCWs_PHs) <- c("City", "Citywide", "BuildingsAverage")

View(compareCWs_PHs)
attach(compareCWs_PHs)

ggplot(compareCWs_PHs, 
       aes(x = Citywide, y = BuildingsAverage)) +
  geom_point(aes(color = "steelblue")) +
  geom_label(aes(label = City, 
                nudge_x=0.45, 
                nudge_y=0.1,
                check_overlap=T))
  geom_abline(aes(intercept = 0, slope = 1)) +
  xlim(0,1)+
  ylim(0,1)+
  xlab("Citywide Green Space Ratio") +
  ylab("Public Housing Green Space Ratio") +
  ggtitle("Comparison of Green Space Surrounding Public Housing vs. At Large in Major US Urban Areas")
