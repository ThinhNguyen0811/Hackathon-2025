package com.demo.resource_request.controller;

import com.demo.resource_request.dto.EmpInfoDto;
import com.demo.resource_request.dto.LogTimeDto;
import com.demo.resource_request.dto.WorkPlanDto;
import com.demo.resource_request.service.ResourceRequestService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequiredArgsConstructor
public class ResourceRequestController {
    private final ResourceRequestService service;

    @GetMapping("/")
    private ResponseEntity<String> hello() {
        return ResponseEntity.ok("API Running...");
    }

    @GetMapping("/empinfo/api/employee/list")
    private ResponseEntity<EmpInfoDto> getAllEmployees() {
        EmpInfoDto dto = service.getAllEmployee();
        return ResponseEntity.ok(dto);
    }

    @GetMapping("/insider/api/booking/byPlanner/{planerId}/{fromDate}/{toDate}")
    private ResponseEntity<List<WorkPlanDto>> getEmployeeWorkPlans(@PathVariable("planerId") String planerId,
                                                      @PathVariable("fromDate") LocalDate fromDate,
                                                      @PathVariable("toDate") LocalDate toDate) {
        List<WorkPlanDto> dto = service.getEmployeeWorkPlans(fromDate, toDate);
        return ResponseEntity.ok(dto);
    }

    @GetMapping("/insider/api/timesheet/list/filter")
    private ResponseEntity<LogTimeDto> getEmployeeLogTimes(@RequestParam("fromDate") LocalDate fromDate,
                                                           @RequestParam("toDate") LocalDate toDate,
                                                           @RequestParam(value = "rate", required = false, defaultValue = "allRate") String rate,
                                                           @RequestParam(value = "status", required = false) String status,
                                                           @RequestParam("skip") Integer skip,
                                                           @RequestParam("take") Integer take,
                                                           @RequestParam("isDescending") Boolean isDescending,
                                                           @RequestParam("sortBy") String date) {
        LogTimeDto dto = service.getEmployeeLogTime(fromDate, toDate, skip, take);
        return ResponseEntity.ok(dto);
    }
}
