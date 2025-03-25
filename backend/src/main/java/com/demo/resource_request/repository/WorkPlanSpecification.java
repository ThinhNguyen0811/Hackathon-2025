package com.demo.resource_request.repository;

import com.demo.resource_request.entity.WorkPlan;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;
import org.springframework.data.jpa.domain.Specification;

import java.time.LocalDate;

@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class WorkPlanSpecification {
    public static Specification<WorkPlan> greaterThanFromDate (LocalDate fromDate) {
        return ((root, query, criteriaBuilder)
                -> criteriaBuilder.greaterThan(root.get("endDate"), fromDate));
    }

    public static Specification<WorkPlan> lessThanToDate (LocalDate toDate) {
        return ((root, query, criteriaBuilder)
                -> criteriaBuilder.lessThan(root.get("startDate"), toDate));
    }
}
