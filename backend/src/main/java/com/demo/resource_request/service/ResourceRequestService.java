package com.demo.resource_request.service;

import com.demo.resource_request.dto.EmpInfoDto;
import com.demo.resource_request.dto.LogTimeDto;
import com.demo.resource_request.dto.WorkPlanDto;
import com.demo.resource_request.entity.Employee;
import com.demo.resource_request.entity.LogTime;
import com.demo.resource_request.entity.WorkPlan;
import com.demo.resource_request.mapper.EmployeeMapper;
import com.demo.resource_request.mapper.LogTimeMapper;
import com.demo.resource_request.mapper.WorkPlanMapper;
import com.demo.resource_request.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional
public class ResourceRequestService {
    private final EmployeeRepository employeeRepo;
    private final WorkPlanRepository workPlanRepo;
    private final LogTimeRepository logTimeRepo;

    private final EmployeeMapper employeeMapper;
    private final WorkPlanMapper workPlanMapper;
    private final LogTimeMapper logTimeMapper;

    public EmpInfoDto getAllEmployee() {
        List<Employee> employees = employeeRepo.findAll();
        return EmpInfoDto.builder()
                .employees(employeeMapper.toDtos(employees))
                .isSyncing(false)
                .lastSyncDate("2025-03-24T00:21:28.8024846Z")
                .build();
    }

    public List<WorkPlanDto> getEmployeeWorkPlans(LocalDate fromDate, LocalDate toDate) {
        Specification<WorkPlan> spec = Specification
                .where(WorkPlanSpecification.greaterThanFromDate(fromDate))
                .and(WorkPlanSpecification.lessThanToDate(toDate));

        List<WorkPlan> workPlans = workPlanRepo.findAll(spec);
        return workPlanMapper.toDtos(workPlans);
    }

    public LogTimeDto getEmployeeLogTime(LocalDate fromDate, LocalDate toDate, Integer skip, Integer take) {
        Specification<LogTime> spec = Specification
                .where(LogTimeSpecification.greaterThanFromDate(fromDate))
                .and(LogTimeSpecification.lessThanToDate(toDate));

        List<LogTime> logTimes = logTimeRepo.findAll(spec);
        return LogTimeDto.builder()
                .result(logTimeMapper.toDtos(logTimes))
                .skip(skip)
                .take(take)
                .terms("")
                .total(logTimes.size())
                .build();
    }
}
