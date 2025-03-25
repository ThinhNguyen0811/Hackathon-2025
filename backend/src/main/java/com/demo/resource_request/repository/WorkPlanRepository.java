package com.demo.resource_request.repository;

import com.demo.resource_request.entity.WorkPlan;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

@Repository
public interface WorkPlanRepository extends JpaRepository<WorkPlan, Integer> , JpaSpecificationExecutor<WorkPlan> {
}
