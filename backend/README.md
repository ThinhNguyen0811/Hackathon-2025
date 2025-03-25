### Run docker compose
```
docker compose up -d
```

### API
1) Get all employee of Empinfor
```
GET http://localhost:8081/empinfo/api/employee/list
```
2) Get workplan of employee
```
GET http://localhost:8081/insider/api/booking/byPlanner/:planerId/:fromDate/:toDate
```
3) Get log time of employee
```
GET http://localhost:8081/insider/api/timesheet/list/filter
```
Request Params
```
fromDate=2025-03-01
toDate=2025-03-04
rate=allRate
status=all
skip=0
take=100000
isDescending=true
sortBy=date
```