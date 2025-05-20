# SQL Query Optimization Tests
This project is created for testing all possible methods that can be employed to improve the performance of database queries, as well as experimenting how each optimization gains any improvements comparing to each other. It focuses on optimizing the (SQL) query statements, tuning database schema, and/or readjusting database structure.

## Technology stack
* Programming language: Python (v3.12)
* Database management system: SQLite
* Web framework: Flask
* Database toolkit: SQLAlchemy (ORM)
* Other libraries: Flask-SQLAlchemy (coding simplicity), Flask-Caching (cache support), uWSGI (app runner)
* Containerization: Docker

## Project setup
Though this project can be set up and run directly like any other Python and Flask projects, this document will walk you through building and running the project in a docker container, which is an easy deployment and a popular method nowadays.

Before starting, you need you set up Docker on the target machine (or instance) you want to host and run the project. Even though Docker is a cross-platform software that can run on a variety of operating systems, Ubuntu Linux is the distro I have selected to use as the evironment of my writing. If your target instance is using the same distro (or any other Ubuntu-based Linux distros), you can refer to this [How-to](https://docs.docker.com/engine/install/ubuntu/) to complete its Docker setup.

### Download project
At first, you need to download the project source code into your local file structure (you might need to have `git` installed on your machine), then switch to the project folder as the following command:
```bash
$> git clone https://github.com/khanhtdk/aggregation-api
$> cd aggregation-api
```

### Build and run project
These following commands respectively show how to build the project into a docker image, and how it is executed to start and run as a container:
```bash
# Build command
$> docker build -t aggregation-api .

# Run command
$> docker run -d -p 5000:5000 --name aggregation-api --env API_SECRET_KEY=123abcxyz aggregation-api
```

> **Notes:** You can set secret key for the API by specifying `--env API_SECRET_KEY=123abcxyz` into the run command above, and changing its value to another more secure string.

## Data ingestion
Before experimenting the tests, you need to ingest the running app with sample data. The file [sales-data.csv](sales-data.csv) existing in this project structure is the data that I have created for this purpose. Here is the command we use to do ingest:

```bash
$> docker exec -it aggregation-api python ingest.py
```

However, if you want to ingest another data from another file — as long as you make it following the structure of the sample file we've discussed above — you can use this command to ingest your file:

```bash
$> docker exec -it aggregation-api python ingest.py --csv-file /path/to/your-sample-data.csv
```

Now the data should be ingested successfully to the application database.

## Application controllers
Controller is where functional logic is implemented and processed. In this project, there are 3 controllers created for handling the aggregation of sales data, they are `MonthlySalesQuery`, `FilteredSalesQuery`, and `TopProductsQuery` respectively. Besides being built to perform a certain task, each controller is also built to have more than one profile where each profile is implemented differently (with or without optimizations) in order to highlight the performance differences among them. 

There is a test script created for each controller and stored in the [tests](tests) folder. It performs test by executing the pre-defined query 200 times, then prints out the total elapsed time in milliseconds. For the sake of accuracy, the controllers are implemented without basing on any ORM layer offered by other database tools (i.e. `SQLAlchemy`) to interact with the database, even though `SQLAlchemy` is also used in this project to simplify the model definitions and facilitate the data ingestion. Instead, each controller directly sends raw SQL query statements to SQLite for execution through the standard `sqlite3` python library.

Performance data of each controller is constructed by running the controller test in 10 times, then the average improvement rates for its profiles are calculated by accumulating those 10 test results. 

Now I'm walking you through the overview of each controller, instructing you how to test it, as well as presenting you some records of its performance data.

### MonthlySalesQuery
This controller aggregates sales data to serve the query of monthly sales revenue. It is implemented having 3 profiles as follows:
* **Profile 1:** Only uses fields that are not indexed, has `year` and `month` fields extracted from the original `date` field using `STRFTIME()` function of SQLite.
* **Profile 2:** Also doesn't rely on any indexes, but here it leverages the pre-populated `year` and `month` fields instead of doing the extraction.
* **Profile 3:** An advanced version of profile 2 — besides using `year` and `month` pre-populated fields, these two fields are also indexed together to form a composite index.

#### SQL statement
This is the query statement being used in each profile except that `{year}` and `{month}` will be populated accordingly with respective fields or functions:

```sqlite
SELECT {year} AS selected_year, {month} AS selected_month, SUM(revenue)
FROM sales
GROUP BY selected_year, selected_month
ORDER BY selected_year, selected_month;
```

#### Test command
This is the command we use to test the performance of this controller:

```bash
$> docker exec -it aggregation-api python -m unittest tests.test_monthly_sales -v
```

Sample output:
```text
test_profile_1 (tests.test_monthly_sales.MonthlySalesQueryController.test_profile_1)
Test MonthlySalesQuery controller: Profile #1 (strftime, no idexes). ... elapsed 156.58ms
ok
test_profile_2 (tests.test_monthly_sales.MonthlySalesQueryController.test_profile_2)
Test MonthlySalesQuery controller: Profile #2 (pre-populated fields). ... elapsed 113.79ms
ok
test_profile_3 (tests.test_monthly_sales.MonthlySalesQueryController.test_profile_3)
Test MonthlySalesQuery controller: Profile #3 (pre-populated fields + indexed). ... elapsed 93.51ms
ok

----------------------------------------------------------------------
Ran 3 tests in 0.366s

OK
```

#### Performance data
According to the following table, we can see that the optimization of **Profile 3** has the largest improvement which is ~48% when compared to the original **Profile 1**:

|                    | Profile 1 | Profile 2  | Profile 3  |
|--------------------|-----------|------------|------------|
| Test #1            | 161.72ms  | 107.99ms   | 82.84ms    |
| Test #2            | 160.06ms  | 127.92ms   | 86.15ms    |
| Test #3            | 161.90ms  | 109.24ms   | 82.43ms    |
| Test #4            | 170.16ms  | 112.11ms   | 87.64ms    |
| Test #5            | 163.51ms  | 117.88ms   | 86.41ms    |
| Test #6            | 164.24ms  | 109.41ms   | 86.10ms    |
| Test #7            | 172.42ms  | 111.72ms   | 88.92ms    |
| Test #8            | 170.96ms  | 119.23ms   | 88.78ms    |
| Test #9            | 154.40ms  | 106.41ms   | 82.24ms    |
| Test #10           | 171.98ms  | 114.85ms   | 87.45ms    |
| **% Avg. Improv.** | **N/A**   | **31.10%** | **47.97%** |

### FilteredSalesQuery
This controller queries and returns records of sales data matching a set of requested filters. Fields that are used as filters consist of `product_name`, `region_name`, `start_date`, and `end_date`.

Like the previous one, this controller is also built having 3 profiles of optimization:
* **Profile 1:** No use of indexes except external fields from the joined tables due to their `UNIQUE` constraints.
* **Profile 2:** Indexes are enabled for all fields that are used for joining and filtering.
* **Profile 3:** Includes optimizations from profile 2 plus partitioning data.

> **Notes:** Due to SQLite limitation of not supporting data partitioning, the data is manually partitioned and stored in 2 separate tables, one table keeps the data of current year and the other keeps the rest. The value of current year is determined by `CURRENT_YEAR_CONTEXT` setting in [config.py](config.py), or it will be calculated using the current time if not defined.

#### SQL statement
The following is a base query statement applied for all profiles except that some fields in the query such as `s.date`, `s.product_id`, and `s.region_id` can be replaced by their indexed versions to support performance tests with indexes of profile number 2 and 3. Besides, for the case of profile 3, if the queried data spans across two tables, two query statements will be created the `UNION ALL` operator is leveraged to combine them together.

```sqlite
SELECT s.date AS date, p.name AS product_name, s.revenue, r.name AS region_name
FROM sales s
JOIN products p ON s.product_id = p.id
JOIN regions r ON s.region_id = r.id
WHERE product_name = '{product_name}' AND region_name = '{region_name}' AND date BETWEEN '{start_date}' AND '{end_date}';
```

> **Notes:** The `WHERE` clause in the statement above is made in full conditions. In reality, it is adjusted to contain just enough conditions depending on what inputs it is given.

#### Test command
```bash
$> docker exec -it aggregation-api python -m unittest tests.test_filtered_sales -v
```

Sample output:
```text
test_profile_1 (tests.test_filtered_sales.FilteredSalesQueryController.test_profile_1)
Test FilteredSalesQuery controller: Profile #1 (no indexes). ... Test FilteredSalesQuery controller: Profile #1 (no indexes): elapsed 77.73ms
ok
test_profile_2 (tests.test_filtered_sales.FilteredSalesQueryController.test_profile_2)
Test FilteredSalesQuery controller: Profile #2 (indexed). ... Test FilteredSalesQuery controller: Profile #2 (indexed): elapsed 72.61ms
ok
test_profile_3 (tests.test_filtered_sales.FilteredSalesQueryController.test_profile_3)
Test FilteredSalesQuery controller: Profile #3 (indexed, partitioning). ... Test FilteredSalesQuery controller: Profile #3 (indexed, partitioning): elapsed 67.10ms
ok

----------------------------------------------------------------------
Ran 3 tests in 0.221s

OK
```

#### Performance data
The optimization for this controller does not gain a significant improvement when profile 2 has improved averagely ~8% and the last profile has ~14%:

|                    | Profile 1 | Profile 2 | Profile 3  |
|--------------------|-----------|-----------|------------|
| Test #1            | 77.73ms   | 72.61ms   | 67.10ms    |
| Test #2            | 72.41ms   | 70.39ms   | 61.94ms    |
| Test #3            | 78.02ms   | 70.05ms   | 65.48ms    |
| Test #4            | 84.25ms   | 73.78ms   | 68.14ms    |
| Test #5            | 84.65ms   | 77.60ms   | 72.94ms    |
| Test #6            | 73.37ms   | 70.29ms   | 71.06ms    |
| Test #7            | 74.38ms   | 67.11ms   | 62.10ms    |
| Test #8            | 73.99ms   | 67.52ms   | 64.51ms    |
| Test #9            | 83.37ms   | 75.36ms   | 69.75ms    |
| Test #10           | 81.61ms   | 73.39ms   | 68.87ms    |
| **% Avg. Improv.** | **N/A**   | **8.28%** | **14.16%** |

> **Thoughts:** There is also another test, which is a denormalized case, where we can make the table directly hold `product_name` and `region_name` to remove the need of joining tables. This technique can gain some performance, however, it can create duplications and may sacrifice integrity.

### TopProductsQuery
This controller queries and returns top products based on sales revenue (aka. best-selling products). Number of products returned is depending on the request value of the parameter `limit` sent to the controller, or 5 if not specified.

In contrast to the above controllers, this one has only two profiles that I can think of for its optimizations, which are:
* **Profile 1:** As usual, this profile has no indexes and no optimizations.
* **Profile 2:** Indexing is enabled for joining fields, grouping and ordering fields.

#### SQL statement
Both profiles share the same query as described below. Field `p.name` has indexing enabled by default because it belongs to `products` table and is defined with `UNIQUE` constraint. While profile #1 doesn't have any indexed fields of its own, profile #2 has indexing enabled for `s.product_id` and a *descending index* created for `s.revenue` for serving data query in descending order.

```sqlite
SELECT p.name AS product_name, SUM(s.revenue) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.id
GROUP BY product_name
ORDER BY total_revenue DESC
LIMIT 5;
```

#### Test command
```bash
$> docker exec -it aggregation-api python -m unittest tests.test_product_topfive -v
```

Sample output:
```text
test_profile_1 (tests.test_product_topfive.TopProductsQueryController.test_profile_1)
Test ProductTopFiveQuery controller: Profile #1 (no idexes). ... elapsed 142.24ms
ok
test_profile_2 (tests.test_product_topfive.TopProductsQueryController.test_profile_2)
Test ProductTopFiveQuery controller: Profile #2 (indexed). ... elapsed 117.35ms
ok

----------------------------------------------------------------------
Ran 2 tests in 0.261s

OK
```

#### Performance data
The optimization of profile #2 by employing indexing only has improved the query performance to averagely ~17%, as follows:

|                    | Profile 1 | Profile 2  |
|--------------------|-----------|------------|
| Test #1            | 142.24ms  | 117.35ms   |
| Test #2            | 141.06ms  | 118.07ms   |
| Test #3            | 141.46ms  | 118.03ms   |
| Test #4            | 137.74ms  | 111.73ms   |
| Test #5            | 136.21ms  | 111.97ms   |
| Test #6            | 136.91ms  | 111.45ms   |
| Test #7            | 136.55ms  | 113.28ms   |
| Test #8            | 131.53ms  | 106.78ms   |
| Test #9            | 135.91ms  | 117.94ms   |
| Test #10           | 129.76ms  | 112.35ms   |
| **% Avg. Improv.** | **N/A**   | **16.81%** |



