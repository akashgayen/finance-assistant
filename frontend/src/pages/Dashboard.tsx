import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import { Stack, Heading, Card, CardBody } from "@chakra-ui/react";
import { Doughnut, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
);

export default function Dashboard() {
  const byCat = useQuery({
    queryKey: ["chart", "byCat"],
    queryFn: async () => (await api.get("/charts/expenses-by-category")).data,
  });
  const trend = useQuery({
    queryKey: ["chart", "trend"],
    queryFn: async () =>
      (
        await api.get("/charts/spend-trend", {
          params: { granularity: "month" },
        })
      ).data,
  });
  return (
    <Stack gap="6">
      <Heading size="md">Overview</Heading>
      <Card.Root>
        <CardBody>{byCat.data && <Doughnut data={byCat.data} />}</CardBody>
      </Card.Root>
      <Card.Root>
        <CardBody>{trend.data && <Line data={trend.data} />}</CardBody>
      </Card.Root>
    </Stack>
  );
}
