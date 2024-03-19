import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from make_packets import make_packets_from_config

import json

class ConfigEditor:
    def __init__(self, master, config):
        self.master = master
        self.config = config
        self.init_ui()
    
    def make_packets(self):
        # Save changes first
        self.save_changes()
        messagebox.showinfo("Please Wait", "Your packets are being made. This may take a while. Please wait...")
        # Then make packets from the current config
        try:
            make_packets_from_config(self.config)
            messagebox.showinfo("Success", "Packets have been successfully made.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to make packets: {e}")


    def init_ui(self):
        self.master.title("MopMan Packet Generator")

        # Adjust the packing of the Notebook to leave space for the buttons at the bottom
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=10, pady=(10, 0))

        # Curriculum tab
        self.curriculum_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.curriculum_frame, text='Curriculum')
        self.init_curriculum_ui()

        # Templates tab
        self.templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.templates_frame, text='Templates Directories')
        self.init_templates_ui()

        # Output directory tab
        self.output_dir_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.output_dir_frame, text='Output Directory')
        self.init_output_dir_ui()

        # Generate tab
        self.generate_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.generate_frame, text='Components to Generate')
        self.init_generate_ui()

        # Frame for buttons
        self.buttons_frame = ttk.Frame(self.master)
        self.buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Save Changes button
        save_button = ttk.Button(self.buttons_frame, text="Save Changes", command=self.save_changes)
        save_button.pack(side=tk.LEFT, padx=(0, 10))

        # Make Packets button
        make_packets_button = ttk.Button(self.buttons_frame, text="Make Packets", command=self.make_packets)
        make_packets_button.pack(side=tk.LEFT)


    def init_curriculum_ui(self):
        self.tree = ttk.Treeview(self.curriculum_frame, columns=('Curriculum Name', 'Record ID', 'Make Packet'), show='headings')
        self.tree.heading('Curriculum Name', text='Curriculum Name')
        self.tree.heading('Record ID', text='Record ID')
        self.tree.heading('Make Packet', text='Make Packet')
        self.tree.column('Curriculum Name', width=600)  # Adjust the width as needed
        self.tree.column('Record ID', width=200)
        self.tree.column('Make Packet', width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_treeview()

        # Add New Curriculum button
        add_curriculum_button = ttk.Button(self.curriculum_frame, text="Add New Curriculum", command=self.add_new_curriculum)
        add_curriculum_button.pack(side=tk.BOTTOM, pady=10)

        # Delete Curriculum button
        delete_curriculum_button = ttk.Button(self.curriculum_frame, text="Delete Curriculum", command=self.delete_curriculum)
        delete_curriculum_button.pack(side=tk.BOTTOM, pady=10)

        self.tree.bind('<Double-1>', self.on_double_click)
        

    def add_new_curriculum(self):
        # Prompt the user for curriculum details
        curriculum_name = simpledialog.askstring("New Curriculum", "Enter the curriculum name:", parent=self.master)
        if not curriculum_name:  # User cancelled or entered an empty name
            return
        record_id = simpledialog.askstring("New Curriculum", "Enter the record ID:", parent=self.master)
        if not record_id:  # User cancelled or entered an empty ID
            return
        make_packet = messagebox.askyesno("New Curriculum", "Make packet for this curriculum?", icon='question', parent=self.master)

        # Update the config dictionary
        self.config['curriculum'][curriculum_name] = {"record_id": record_id, "make_packet": make_packet}

        # Update the Treeview
        self.populate_treeview()

    def delete_curriculum(self):
        selected_items = self.tree.selection()
        if selected_items:  # Check if there is a selected item
            item_id = selected_items[0]
            # Confirm deletion with the user
            if messagebox.askyesno("Delete Curriculum", "Are you sure you want to delete this curriculum?"):
                # Remove from Treeview
                self.tree.delete(item_id)
                # Remove from config dictionary
                if item_id in self.config['curriculum']:
                    del self.config['curriculum'][item_id]


    def populate_treeview(self):
        for meeting in self.tree.get_children():
            self.tree.delete(meeting)
        for meeting, details in self.config['curriculum'].items():
            make_packet = '✓' if details['make_packet'] else '✗'
            self.tree.insert('', tk.END, iid=meeting, values=(meeting, details['record_id'], make_packet))

    def on_double_click(self, event):
        selected_items = self.tree.selection()
        if not selected_items:  # No item selected
            return
        item_id = selected_items[0]
        column = self.tree.identify_column(event.x)
        column_no = int(column.replace('#', ''))

        if column_no == 3:  # Make Packet column
            current_value = self.config['curriculum'][item_id]['make_packet']
            self.config['curriculum'][item_id]['make_packet'] = not current_value
            self.populate_treeview()
        else:
            entry = ttk.Entry(self.master)
            entry.insert(0, self.tree.set(item_id, column))
            entry.place(x=event.x, y=event.y, width=200)  # Adjust width as needed

            def save_edit(event):
                new_value = entry.get()
                if column_no == 2:  # Record ID
                    self.config['curriculum'][item_id]['record_id'] = new_value
                self.populate_treeview()
                entry.destroy()

            entry.bind('<Return>', save_edit)
            entry.bind('<FocusOut>', lambda e: entry.destroy())
            entry.focus()


    def init_templates_ui(self):
        for template_name, template_path in self.config['templates'].items():
            label = ttk.Label(self.templates_frame, text=template_name)
            label.pack(side=tk.TOP, anchor='w')
            entry = ttk.Entry(self.templates_frame)
            entry.insert(0, template_path)
            entry.pack(side=tk.TOP, fill=tk.X, expand=True)
            entry.bind('<FocusOut>', lambda e, name=template_name: self.update_template_path(name, e.widget.get()))
            entry.bind('<Return>', lambda e, name=template_name: self.update_template_path(name, e.widget.get()))

    def update_template_path(self, name, path):
        self.config['templates'][name] = path


    def init_output_dir_ui(self):
        label = ttk.Label(self.output_dir_frame, text="Output Directory")
        label.pack(side=tk.TOP, anchor='w')
        entry = ttk.Entry(self.output_dir_frame)
        entry.insert(0, self.config['output_dir'])
        entry.pack(side=tk.TOP, fill=tk.X, expand=True)
        entry.bind('<FocusOut>', lambda e: self.update_output_dir(e.widget.get()))
        entry.bind('<Return>', lambda e: self.update_output_dir(e.widget.get()))

    def update_output_dir(self, path):
        self.config['output_dir'] = path


    def init_generate_ui(self):
        for option, value in self.config['generate'].items():
            check_var = tk.BooleanVar(value=value)
            check_button = ttk.Checkbutton(self.generate_frame, text=option, variable=check_var, onvalue=True, offvalue=False)
            check_button.pack(side=tk.TOP, anchor='w')
            check_button.bind('<Button-1>', lambda e, name=option, var=check_var: self.update_generate_option(name, var))

    def update_generate_option(self, name, var):
        self.config['generate'][name] = var.get()


    def save_changes(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
        messagebox.showinfo("Save", "Changes have been saved to config.json.")


def center_window(root, width=800, height=600):
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position x, y
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def main():
    root = tk.Tk()
    center_window(root, 1000, 600)

    # Load the configuration from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    app = ConfigEditor(root, config)
    root.mainloop()

if __name__ == "__main__":
    main()
