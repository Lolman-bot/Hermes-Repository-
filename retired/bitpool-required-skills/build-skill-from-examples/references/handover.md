# Handover to /create-new-skill (step 7)

This skill writes the skill. `/create-new-skill` puts it in the `Lolman-bot/Hermes-Repository-` repo.
Don't duplicate its steps here: the branch, the README catalogue row, `/update-hermes-skill`, the
readiness check and the pull request all belong to it, and follow the repo's house rules as they
stand on the day.

## On the machine with the repo (CLI, TUI, desktop app)

1. Make sure the finished, approved folder is on disk at
   `$HERMES_HOME/build-skill/<skill-name>/skill/`.
2. Load `/create-new-skill` (`skill_view(name="create-new-skill")`) and tell it plainly where this is
   coming from:

   > "Arriving from /build-skill-from-examples. The skill is written and approved by the user. The
   > folder is at `$HERMES_HOME/build-skill/<skill-name>/skill/`. Skip choosing a route and
   > drafting; start where the finished folder goes into the repo."

3. `/create-new-skill` takes it from there. Its rule about one pull request, only after the user
   says it's finished, applies as usual.

## From a messaging app, or a Hermes with no repo access

A pull request needs a machine with `gh` signed in and the repo cloned. If the Hermes the person is
talking to can't reach the repo (no `gh`, no clone, or no access), don't try to push from it:

1. Zip the finished folder with `terminal` (`python -m zipfile -c <skill-name>.zip <folder>`) and
   send it as an attachment with `MEDIA:<absolute path to the zip>` in the reply.
2. Tell them, in plain words: "Your skill's written. To get it into the repo, open Hermes on a
   computer with the repo set up, unzip this somewhere, run `/create-new-skill`, and say it's
   arriving from build-skill-from-examples with the folder at that path. It'll pick up from putting
   it in the repo."
3. Stop there.

## Clean-up

The `$HERMES_HOME/build-skill/<skill-name>/` working folder (seed, diagram, canvas file, draft) is
scratch. Once `/create-new-skill` has copied the skill into the repo, offer to delete it. Never
commit it.
