import ResourceRequests from "../components/ResourceRequests";
import EmployeesTable from "../components/EmployeesTable";

export default function IndexPage() {
  return (
      <div>
        <h1 className="text-2xl font-bold mb-4">Resource Requests</h1>
        <ResourceRequests />
      </div>
  )
}