#install.packages(c('quantmod','tidyverse','ff','foreign','R.matlab', "clusrank"),dependency=T)
library(clusrank)
all_data <- read.csv("r_data.csv")

#all_data$seller_FE_id <- paste(as.character(all_data$session),as.character(all_data$worker_id),all_data$Treatment)
#min(all_data$seller_profit_share)

#round_number=round_number+1 because it was fixed
round1_data <- all_data[all_data$round_number == 2, ]
clusWilcox.test(wage ~ treatment+cluster(firm_identification), data=round1_data)



clusWilcox.test(effort ~ treatment+cluster(session), data=all_data)
clusWilcox.test(total_surplus ~ treatment+cluster(session), data=all_data)
clusWilcox.test(wage ~ treatment+cluster(worker_identification), data=all_data)


clusWilcox.test(effort ~ treatment+cluster(worker_identification), data=all_data)
clusWilcox.test(wage ~ treatment+cluster(firm_identification), data=all_data)
clusWilcox.test(worker_surplus ~ treatment+cluster(worker_identification), data=all_data)
clusWilcox.test(firm_surplus ~ treatment+cluster(worker_identification), data=all_data)
clusWilcox.test(total_surplus ~ treatment+cluster(worker_identification), data=all_data)
clusWilcox.test(worker_surplus_share ~ treatment+cluster(worker_identification), data=all_data)

