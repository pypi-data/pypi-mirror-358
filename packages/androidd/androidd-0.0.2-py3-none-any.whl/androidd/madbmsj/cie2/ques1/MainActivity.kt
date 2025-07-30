package com.example.cie_que1

import android.content.Intent
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.view.MenuInflater
import android.view.View
import android.widget.*

class MainActivity : AppCompatActivity() {

    val books = listOf("Data Structures", "Operating Systems", "Machine Learning", "Thermodynamics", "Digital Logic")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val bookListView = findViewById<ListView>(R.id.bookListView)
        val btnMenu = findViewById<Button>(R.id.btnMenu)

        val adapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, books)
        bookListView.adapter = adapter

        bookListView.setOnItemClickListener { _, _, position, _ ->
            val intent = Intent(this, SecondActivity::class.java)
            intent.putExtra("book_name", books[position])
            startActivity(intent)
        }

        btnMenu.setOnClickListener { v ->
            showPopupMenu(v)
        }
    }

    private fun showPopupMenu(view: View) {
        val popup = PopupMenu(this, view)
        val inflater: MenuInflater = popup.menuInflater
        inflater.inflate(R.menu.department_menu, popup.menu)
        popup.setOnMenuItemClickListener { item ->
            Toast.makeText(this, "Department: ${item.title}", Toast.LENGTH_SHORT).show()
            true
        }
        popup.show()
    }
}
