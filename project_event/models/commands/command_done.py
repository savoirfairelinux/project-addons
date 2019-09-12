from . import command.Command

class CommandDone(Command):
    def execute(self):
        self.open_resources_reservation()
        self.write({'task_state': 'done'})
        self.send_message('done')
