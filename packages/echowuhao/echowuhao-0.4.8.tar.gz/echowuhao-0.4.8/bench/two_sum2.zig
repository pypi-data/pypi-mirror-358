const std = @import("std");

fn twoSum(numbers: []const i32, target: i32) ?[2]usize {
    var seen = std.AutoHashMap(i32, usize).init(std.heap.page_allocator);
    defer seen.deinit();

    for i, number in numbers {
        const complement = target - number;

        if (seen.get(complement)) |j| {
            return [j, i];
        }

        seen.put(number, i) catch unreachable;
    }

    return null;
}

pub fn main() void {
    const numbers = [1, 2, 3, 4, 5];
    const target = 7;

    if (twoSum(&numbers, target)) |indices| {
        std.debug.print("Indices: {} and {}\n", .{ indices[0], indices[1] });
    } else {
        std.debug.print("No solution found\n", .{});
    }
}
