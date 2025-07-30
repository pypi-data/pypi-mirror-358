const std = @import("std");

pub fn twoSum(nums: []const i32, target: i32) ![]const i32 {
    var seen = std.AutoHashMap(i32, i32).init(std.heap.page_allocator);
    defer seen.deinit();

    for (0.., nums) |i, num| {
        const complement = target - num;
        if (seen.get(complement)) |index| {
            return &[_]i32{ index, @intCast(i) };
        } else {
            seen.put(num, @intCast(i)) catch unreachable;
        }
    }

    return error.NotFound;
}

pub fn main() !void {
    const nums = [_]i32{ 2, 7, 11, 15 };
    const target = 9;

    const result = twoSum(&nums, target) catch |err| {
        std.debug.print("Error: {}\n", .{err});
        return;
    };

    std.debug.print("Indices: [{} {}]\n", .{ result[0], result[1] });
}
