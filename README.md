# add_match_scrawl_project
2016.5

solved problem:1 )conflict district 2)分词问题 所有命名实体字典 所有道路 爬取 bad case 上海南汇市（上海还是海南）  字典中加入省市 3）错别字 丢字 黄海路 黄海一路 切碎点 
4）经纬度->千米   5)太多广东省深圳市，去掉只有省市的,去掉冲突的  xx路xx区  6）bad case 滨城路 geo判断去掉了 但字符串是被包含的  设定这种情况下不听geo的 includedString判断为准 7)地址一次找不到试向前搜索多次尝试
