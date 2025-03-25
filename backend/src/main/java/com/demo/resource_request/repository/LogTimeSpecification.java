package com.demo.resource_request.repository;

import com.demo.resource_request.entity.LogTime;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;
import org.springframework.data.jpa.domain.Specification;

import java.time.LocalDate;

@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class LogTimeSpecification {
    public static Specification<LogTime> greaterThanFromDate (LocalDate fromDate) {
        return ((root, query, criteriaBuilder)
                -> criteriaBuilder.greaterThan(root.get("logDate"), fromDate));
    }

    public static Specification<LogTime> lessThanToDate (LocalDate toDate) {
        return ((root, query, criteriaBuilder)
                -> criteriaBuilder.lessThan(root.get("logDate"), toDate));
    }
}
