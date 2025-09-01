import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import {
  Table,
  Stack,
  Button,
  Input,
  HStack,
  Text,
  Dialog,
  Portal,
} from "@chakra-ui/react";
import NewTransaction from "../components/NewTransaction";

type Transaction = {
  id: string;
  occurred_at: string;
  type: string;
  amount: number;
  merchant?: string;
};

type TransactionsResponse = {
  items: Transaction[];
  total: number;
};

export default function Transactions() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const pageSize = 10;

  const params: Record<string, any> = { page, page_size: pageSize };
  if (search.trim()) params.search = search.trim();

  const { data, isPending, isError } = useQuery<TransactionsResponse>({
    queryKey: ["tx", { page, search: search.trim() || null }],
    queryFn: async () => (await api.get("/transactions", { params })).data,
  });

  return (
    <Stack gap="4">
      <Dialog.Root>
        <HStack justify="space-between" align="start">
          <HStack>
            <Input
              placeholder="Search merchant/notes"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <Button onClick={() => setPage(1)}>Filter</Button>
          </HStack>

          <Dialog.Trigger asChild>
            <Button colorScheme="blue">New</Button>
          </Dialog.Trigger>
        </HStack>

        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content maxW="lg">
              <Dialog.Header>
                <Dialog.Title>New Transaction</Dialog.Title>
              </Dialog.Header>
              <Dialog.Body>
                <NewTransaction />
              </Dialog.Body>
              <Dialog.CloseTrigger />
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>

      {isError && <Text color="red.500">Failed to load transactions</Text>}

      <Table.Root size="sm">
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>Date</Table.ColumnHeader>
            <Table.ColumnHeader>Type</Table.ColumnHeader>
            <Table.ColumnHeader textAlign="end">Amount</Table.ColumnHeader>
            <Table.ColumnHeader>Merchant</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {!isPending &&
            data?.items?.map((it) => (
              <Table.Row key={it.id}>
                <Table.Cell>
                  {new Date(it.occurred_at).toLocaleString()}
                </Table.Cell>
                <Table.Cell>{it.type}</Table.Cell>
                <Table.Cell textAlign="end">{it.amount}</Table.Cell>
                <Table.Cell>{it.merchant || "-"}</Table.Cell>
              </Table.Row>
            ))}
        </Table.Body>
      </Table.Root>

      <HStack justify="space-between">
        <Button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Prev
        </Button>
        <Text>Page {page}</Text>
        <Button
          onClick={() => setPage((p) => p + 1)}
          disabled={!!data && page * pageSize >= data.total}
        >
          Next
        </Button>
      </HStack>
    </Stack>
  );
}
