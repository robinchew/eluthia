%% -*- erlang -*-

main(Args) ->
    [Path] = Args,
    PackageName = case file:consult(Path) of
        {ok, Config} ->
            {value, {release, {Name, Version},  _}} = lists:search(fun({release, _, _}) -> true;(_) -> false end, Config),
            "[\"" ++ atom_to_list(Name) ++ "\", \"" ++ Version ++ "\"]"
    end,
    io:format("~s", [PackageName]).
