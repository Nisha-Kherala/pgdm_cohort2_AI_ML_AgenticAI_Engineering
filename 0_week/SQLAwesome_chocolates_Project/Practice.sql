#Q1 BASIC FILTERING
-- SELECT SPID, PID, SaleDate, Amount, Customers,Boxes
-- from sales
-- where Amount > 10000;
-- ------------------------------------------------------------
#Q2 Sorting and Filtering
-- SELECT SaleDate, SPID, PID, Boxes, Amount
-- FROM sales
-- where Boxes > 500
-- ORDER BY Boxes DESC;
-- ------------------------------------------------------------
#Q3 DISTINCT + Date Filtering
-- SELECT DISTINCT PID 
-- FROM sales
-- WHERE YEAR(SaleDate) = 2021
-- ------------------------------------------------------------
#Find percentage of orders from each region
-- SELECT g.Region, count(*)/(select count(*) from sales)*100 as perc_order_per_region
-- FROM sales s
-- LEFT JOIN geo g ON s.GeoID=g.GeoID
-- group by Region
-- ------------------------------------------------------------
# Find the second top sales person as per total orders
-- WITH cte AS (SELECT s.SPID,p.Salesperson, count(*) as Tot_orders
--  FROM sales s
--  LEFT JOIN people p ON s.SPID=p.SPID
--  GROUP BY s.SPID),
-- cte2 AS (SELECT Salesperson,SPID, DENSE_RANK() OVER(ORDER BY Tot_orders DESC) as rnk  FROM cte)
-- SELECT Salesperson,SPID FROM cte2
-- where rnk = 2
-- ------------------------------------------------------------
#Alternate Solution
-- SELECT SPID,COUNT(*) FROM sales
-- GROUP BY SPID
-- ORDER BY COUNT(*) DESC
-- LIMIT 1 OFFSET 1
-- ------------------------------------------------------------
#Find the monthly revenue, and total sales for each region
-- SELECT g.Region as Region,MONTH(s.SaleDate) as Month, SUM(Amount) as MonthlyRevenue
-- FROM sales s
-- LEFT JOIN geo g ON s.GeoID=g.GeoID
-- GROUP BY g.Region, MONTH(s.SaleDate)
-- ------------------------------------------------------------
#Q4 Basic Aggregation
-- SELECT sum(Amount) as Total_sales,avg(Amount) as Average_sales,max(Amount) as Maximum_sales, sum(Boxes) as Total_box_sold, count(Distinct Customers) as Total_Customers  
-- FROM sales
-- ------------------------------------------------------------
#Q5 Sales by Product
-- SELECT PID,SUM(Amount) as TotalSales, SUM(Boxes) as TotalBoxes FROM sales
-- GROUP BY PID
-- ORDER BY TotalSales DESC
-- ------------------------------------------------------------
#Q6 Sales by Product with HAVING
-- SELECT PID,SUM(Amount) as TotSales FROM sales
-- GROUP BY PID
-- HAVING SUM(Amount)>500000
-- ORDER BY TotSales DESC
-- ------------------------------------------------------------
#Q7 Sales by Region
-- SELECT Region,SUM(Amount) as TotalSales
-- FROM sales s
-- INNER JOIN geo g ON s.GeoID=g.GeoID
-- GROUP BY Region
-- ORDER BY SUM(Amount) DESC
-- ------------------------------------------------------------
#Q8 Sales by Country
-- SELECT Geo,SUM(Amount) as TotSales,SUM(Boxes) as TotBoxes,COUNT(Customers) as TotCust 
-- FROM sales s
-- INNER JOIN geo g ON s.GeoID=g.GeoID
-- GROUP BY Geo
-- ORDER BY TotSales DESC
-- ------------------------------------------------------------
#Q9 Salesperson Performanc
-- SELECT Salesperson,s.SPID,Team,SUM(Amount) as TotSales
-- FROM sales s
-- JOIN people p ON s.SPID=p.SPID
-- GROUP BY Salesperson,s.SPID
-- ORDER BY TotSales DESC
-- ------------------------------------------------------------
#Q10 Product Category Analysis
-- SELECT Category,SUM(Amount) as TotSales,SUM(Boxes) as TotBoxes
-- FROM sales s
-- JOIN products p ON s.PID=p.PID
-- GROUP BY Category
-- ORDER BY TotSales DESC
-- ------------------------------------------------------------
#Q11 Team Performance
-- SELECT p.Team, COUNT(*) as NoOfTrans,SUM(s.Amount) as TotSales, SUM(s.Boxes) as TotalBoxes
-- FROM sales s
-- LEFT JOIN people p ON s.SPID=p.SPID
-- GROUP BY p.Team
-- ORDER BY SUM(s.Amount) Desc
-- ------------------------------------------------------------
#Q12 Monthly Sales
-- SELECT MONTHNAME(SaleDate) as Month,SUM(Amount) as TotSales, SUM(Boxes) as TotalBoxes
-- FROM sales
-- WHERE YEAR(SaleDate)=2021
-- GROUP BY MONTHNAME(SaleDate)
-- ORDER BY MONTHNAME(SaleDate)
-- ------------------------------------------------------------
#Q13 Product Cost Analysis
-- SELECT s.PID,p.Product,p.Cost_per_box,SUM(s.Boxes) as TotBoxes, SUM(s.Boxes)*p.Cost_per_box as EstiProdCost
-- FROM sales s
-- JOIN products p
-- on s.PID=p.PID
-- GROUP BY s.PID,p.Product,p.Cost_per_box
-- ORDER BY EstiProdCost DESC
-- ------------------------------------------------------------
#Q14 Revenue per Box
-- SELECT Product,SUM(Amount) as TotSales, SUM(Boxes) as TotBox,(SUM(s.Amount) / NULLIF(SUM(s.Boxes), 0)) AS RevenuePerBox
-- FROM sales s
-- JOIN products p
-- on s.PID=p.PID
-- GROUP BY Product
-- ORDER BY RevenuePerBox DESC
-- ------------------------------------------------------------
#Q15 Salesperson and Region Analysis
-- SELECT Region,p.Salesperson,p.Team,SUM(Amount) as TotSal
-- FROM sales s
-- JOIN people p ON s.SPID=p.SPID
-- JOIN geo g ON s.GeoID=g.GeoID
-- GROUP BY Region,p.Salesperson,p.Team
-- ORDER BY Region,TotSal DESC
-- ------------------------------------------------------------
#Q16 High-Value Transactions by Category
-- SELECT p.Category,AVG(s.Amount) AS Avg_trans_amt,SUM(s.Amount) AS Tot_sales FROM sales s
-- LEFT JOIN products p ON s.PID=p.PID
-- GROUP BY p.Category
-- HAVING AVG(s.Amount)>8000
-- -- ------------------------------------------------------------
#Q17 Salesperson Performance Classification
-- WITH SalespersonTotals AS (SELECT p.Salesperson,p.Team,SUM(s.Amount) as TotSales
-- FROM sales s
-- JOIN people p ON s.SPID=p.SPID
-- GROUP BY p.Salesperson,p.Team)

-- SELECT *,CASE WHEN TotSales>=1000000 THEN 'Excellent'
--                 WHEN TotSales>=500000 THEN 'Good'
--                 ELSE 'Needs Improvement'
--                 END AS Performance
-- FROM SalespersonTotals
-- ORDER BY TotSales DESC
-- -- ------------------------------------------------------------
#Q18 Top 3 Salespeople in Each Region
-- WITH RankedRegionalSales AS (SELECT g.Region,p.Salesperson,SUM(s.Amount) as TotSals, 
--             RANK() OVER(PARTITION BY g.Region ORDER BY SUM(s.Amount) DESC) AS RegionalRank
-- FROM sales s
-- JOIN people p ON s.SPID=p.SPID
-- JOIN geo g ON s.GeoID=g.GeoID
-- GROUP BY g.Region,p.Salesperson)

-- SELECT Region,Salesperson,TotSals,RegionalRank
-- FROM RankedRegionalSales
-- WHERE RegionalRank<4
-- ------------------------------------------------------------
-- Q19. Top 2 Products in Each Category
-- WITH RankedProductsInCategory AS (SELECT p.Category,p.Product,SUM(s.Amount) as Total_Sales,
--               SUM(s.Boxes) AS Total_Boxes,
--               DENSE_RANK() OVER(PARTITION BY p.Category ORDER BY SUM(s.Amount) DESC) as Category_Rank
--               FROM sales s
--               JOIN products p ON s.PID=p.PID
--               GROUP BY p.Category,p.Product)

-- SELECT Category,Product,Total_Sales,Total_Boxes,Category_Rank
-- FROM RankedProductsInCategory
-- WHERE Category_Rank <3
-- ORDER BY Category
-- ------------------------------------------------------------
#Q20 Advanced Business Performance Analysis
-- WITH ProductPerformance AS (SELECT p.Product,p.Category,p.Size,SUM(s.Amount) as TotalSales,SUM(s.Boxes) AS TotalBoxesSold,
--             COUNT(*) AS TotalCustomers, AVG(Amount) AS AverageTransactionAmount,
--             SUM(s.Amount)/NULLIF(SUM(s.Boxes),0) AS RevenuePerBox,
--             (SUM(s.Boxes)*Cost_per_box) AS EstimatedProductCost,
--             (SUM(s.Amount) - (SUM(s.Boxes) * p.Cost_per_box)) AS EstimatedProfit,
--             DENSE_RANK() OVER (PARTITION BY p.Category ORDER BY SUM(s.Amount) DESC) AS SalesRank
-- FROM sales s
-- JOIN products p ON s.PID=p.PID
-- GROUP BY p.Product,p.Category,p.Size,p.Cost_per_box)

-- SELECT Product,Category,Size,TotalSales,TotalBoxesSold,TotalCustomers,
--     AverageTransactionAmount,RevenuePerBox,EstimatedProductCost,EstimatedProfit,SalesRank
-- FROM ProductPerformance
-- WHERE 
--     SalesRank < 3
-- ORDER BY 
--     Category, 
--     SalesRank



