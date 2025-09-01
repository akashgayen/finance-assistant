// src/components/NewTransaction.tsx
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import {
  Card,
  CardBody,
  Stack,
  HStack,
  Input,
  Textarea,
  Button,
  Text,
  Heading,
  Select,
  createListCollection,
  Portal,
  NativeSelect,
} from "@chakra-ui/react";

type Category = { id: string; name: string };

const typeOptions = createListCollection({
  items: [
    { label: "Expense", value: "expense" },
    { label: "Income", value: "income" },
  ],
});

export default function NewTransaction() {
  const qc = useQueryClient();

  // basic form state
  const [type, setType] = useState<"income" | "expense">("expense");
  // Select.Root in v3 expects string[] when controlled; keep a single selection array
  const [typeSel, setTypeSel] = useState<string[]>([type]);

  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("INR");
  const [occurredAt, setOccurredAt] = useState(""); // HTML datetime-local
  const [categoryId, setCategoryId] = useState<string>("");
  const [merchant, setMerchant] = useState("");
  const [notes, setNotes] = useState("");
  const [err, setErr] = useState("");

  // categories for the select
  const categories = useQuery({
    queryKey: ["categories"],
    queryFn: async () => (await api.get("/categories")).data as Category[],
  });
  const allowed = ["income", "expense"] as const;
  type TxType = (typeof allowed)[number];

  const createTx = useMutation({
    mutationFn: async () => {
      const iso = occurredAt
        ? new Date(occurredAt).toISOString()
        : new Date().toISOString();
      return (
        await api.post("/transactions", {
          type,
          amount: Number(amount),
          currency,
          category_id: categoryId || null,
          merchant: merchant || null,
          notes: notes || null,
          occurred_at: iso,
        })
      ).data;
    },
    onSuccess: async () => {
      // reset form and refresh transactions list
      setAmount("");
      setMerchant("");
      setNotes("");
      setCategoryId("");
      await qc.invalidateQueries({ queryKey: ["tx"] });
    },
    onError: () => setErr("Could not create transaction"),
  });

  const submit = () => {
    setErr("");
    if (!amount || Number(amount) <= 0 || !occurredAt) {
      setErr("Amount and date are required");
      return;
    }
    createTx.mutate();
  };

  return (
    <Card.Root>
      <CardBody>
        <Stack gap="3">
          <Heading size="sm">New Transaction</Heading>
          {err && <Text color="red.500">{err}</Text>}

          {/* Type, Amount, Currency */}
          <HStack gap="3" align="start">
            {/* Chakra v3 Select.Root (single selection via string[]) */}
            <Select.Root
              collection={typeOptions}
              value={typeSel}
              onValueChange={(e) => {
                const [first] = e.value; // e.value is string[]
                if (allowed.includes(first as TxType)) {
                  const v = first as TxType;
                  setType(v);
                  setTypeSel([v]); // keep Select.Root controlled value as one-element array
                }
              }}
              width="200px"
            >
              <Select.HiddenSelect />
              <Select.Label>Type</Select.Label>
              <Select.Control>
                <Select.Trigger>
                  <Select.ValueText placeholder="Choose type" />
                </Select.Trigger>
                <Select.IndicatorGroup>
                  <Select.Indicator />
                </Select.IndicatorGroup>
              </Select.Control>
              <Portal>
                <Select.Positioner>
                  <Select.Content>
                    {typeOptions.items.map((opt) => (
                      <Select.Item item={opt} key={opt.value}>
                        {opt.label}
                        <Select.ItemIndicator />
                      </Select.Item>
                    ))}
                  </Select.Content>
                </Select.Positioner>
              </Portal>
            </Select.Root>

            <Input
              type="number"
              step="0.01"
              placeholder="Amount"
              value={amount}
              onChange={(e) => setAmount(e.currentTarget.value)}
            />
            <Input
              placeholder="Currency"
              value={currency}
              onChange={(e) => setCurrency(e.currentTarget.value)}
              width="120px"
            />
          </HStack>

          {/* Date/Time and Category */}
          <HStack gap="3">
            <Input
              type="datetime-local"
              value={occurredAt}
              onChange={(e) => setOccurredAt(e.currentTarget.value)}
            />
            {/* Simple single-value select via NativeSelect */}
            <NativeSelect.Root width="240px">
              <NativeSelect.Field
                value={categoryId}
                onChange={(e) => setCategoryId(e.currentTarget.value)}
              >
                <option value="">Category (optional)</option>
                {categories.data?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </NativeSelect.Field>
              <NativeSelect.Indicator />
            </NativeSelect.Root>
          </HStack>

          <Input
            placeholder="Merchant"
            value={merchant}
            onChange={(e) => setMerchant(e.currentTarget.value)}
          />
          <Textarea
            placeholder="Notes"
            value={notes}
            onChange={(e) => setNotes(e.currentTarget.value)}
          />

          <HStack>
            <Button
              colorScheme="blue"
              onClick={submit}
              loading={createTx.isPending}
            >
              Add
            </Button>
            {createTx.isSuccess && <Text color="green.600">Saved</Text>}
          </HStack>
        </Stack>
      </CardBody>
    </Card.Root>
  );
}
