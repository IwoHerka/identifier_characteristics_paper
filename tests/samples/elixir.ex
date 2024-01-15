defmodule Foo do
  def foo(arg1, arg2) do
    arg1 + arg2.()
  end

  defp bar(arg1, arg2) do
    arg1 + arg2.()
  end
end


add = fn a, b -> a + b end
result = add.(1, 2)


defmodule Bar do
  def func(x) when is_number(x) do
    x ** 2
  end

  def func(x) when is_list(x) do
    x ** 2
  end
end


add = &(&1 + &2)
result = add.(1, 2)


defmodule Bar do
  def func(a), do: a
  def func(a, b), do: a + b
end
